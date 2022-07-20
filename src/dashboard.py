"""
< WGDashboard > - Copyright(C) 2021 Donald Zou [https://github.com/donaldzou]
Under Apache-2.0 License
"""

import hashlib
import json

# Python Built-in Library
import os
import secrets
import subprocess
import urllib.parse
import urllib.request
import urllib.error

# PIP installed library
import ifcfg
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    session,
    jsonify,
    g,
)
from flask_qrcode import QRcode
from icmplib import ping, traceroute

# Dashboard Version
DASHBOARD_VERSION = "v3.0.6"

# WireGuard's configuration path
WG_CONF_PATH = None

# Dashboard Config Name
CONFIGURATION_PATH = os.getenv("CONFIGURATION_PATH", ".")
DB_PATH = os.path.join(CONFIGURATION_PATH, "db")
if not os.path.isdir(DB_PATH):
    os.mkdir(DB_PATH)
DASHBOARD_CONF_FILE = os.path.join(CONFIGURATION_PATH, "wg-dashboard.ini")

# Upgrade Required
UPDATE = None

# Flask App Configuration
app = Flask("WGDashboard")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 5206928
app.secret_key = secrets.token_urlsafe(16)
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Enable QR Code Generator
QRcode(app)

# (NB) It is important to import these after the app is created
import wg, util, rest_routes


# TODO: use class and object oriented programming


"""
Flask Functions
"""


@app.teardown_request
def close_DB(exception):
    """
    Commit to the database for every request
    @param exception: Exception
    @return: None
    """
    if hasattr(g, "db"):
        g.db.commit()
        g.db.close()


@app.before_request
def auth_req():
    """
    Action before every request
    @return: Redirect
    """
    if getattr(g, "db", None) is None:
        g.db = util.connect_db(CONFIGURATION_PATH)
    g.DASHBOARD_CONF_FILE = DASHBOARD_CONF_FILE
    g.WG_CONF_PATH = WG_CONF_PATH
    g.DB_PATH = DB_PATH
    g.CONFIGURATION_PATH = CONFIGURATION_PATH
    g.cur = g.db.cursor()
    g.conf = read_and_update_config_file()
    req = g.conf.get("Server", "auth_req")
    session["update"] = UPDATE
    session["dashboard_version"] = DASHBOARD_VERSION
    if req == "true":
        if (
            "/static/" not in request.path
            and request.endpoint != "signin"
            and request.endpoint != "signout"
            and request.endpoint != "auth"
            and "username" not in session
        ):
            app.logger.info(
                "User not signed in - Attempted access: " + str(request.endpoint)
            )
            if request.endpoint != "index":
                session["message"] = "You need to sign in first!"
            else:
                session["message"] = ""
            redirectURL = str(request.url)
            redirectURL = redirectURL.replace("http://", "")
            redirectURL = redirectURL.replace("https://", "")
            return redirect("/signin?redirect=" + redirectURL)
    else:
        if request.endpoint in [
            "signin",
            "signout",
            "auth",
            "settings",
            "update_acct",
            "update_pwd",
            "update_app_ip_port",
            "update_wg_conf_path",
        ]:
            return redirect(url_for("index"))
    return None


"""
Sign In / Sign Out
"""


@app.route("/signin", methods=["GET"])
def signin():
    """
    Sign in request
    @return: template
    """

    message = ""
    if "message" in session:
        message = session["message"]
        session.pop("message")
    return render_template("signin.html", message=message, version=DASHBOARD_VERSION)


# Sign Out
@app.route("/signout", methods=["GET"])
def signout():
    """
    Sign out request
    @return: redirect back to sign in
    """
    if "username" in session:
        session.pop("username")
    return redirect(url_for("signin"))


@app.route("/auth", methods=["POST"])
def auth():
    """
    Authentication request
    @return: json object indicating verifying
    """
    data = request.get_json()
    config = g.conf
    password = hashlib.sha256(data["password"].encode())
    if (
        password.hexdigest() == config["Account"]["password"]
        and data["username"] == config["Account"]["username"]
    ):
        session["username"] = data["username"]
        config.clear()
        return jsonify({"status": True, "msg": ""})
    config.clear()
    return jsonify({"status": False, "msg": "Username or Password is incorrect."})


"""
Index Page
"""


@app.route("/", methods=["GET"])
def index():
    """
    Index page related
    @return: Template
    """
    msg = ""
    if "switch_msg" in session:
        msg = session["switch_msg"]
        session.pop("switch_msg")

    return render_template("index.html", conf=util.get_conf_list(WG_CONF_PATH), msg=msg)


# Setting Page
@app.route("/settings", methods=["GET"])
def settings():
    """
    Settings page related
    @return: Template
    """
    message = ""
    status = ""
    config = g.conf
    if "message" in session and "message_status" in session:
        message = session["message"]
        status = session["message_status"]
        session.pop("message")
        session.pop("message_status")
    required_auth = config.get("Server", "auth_req")
    return render_template(
        "settings.html",
        conf=util.get_conf_list(WG_CONF_PATH),
        message=message,
        status=status,
        app_ip=config.get("Server", "app_ip"),
        app_port=config.get("Server", "app_port"),
        required_auth=required_auth,
        wg_conf_path=config.get("Server", "wg_conf_path"),
        peer_global_DNS=config.get("Peers", "peer_global_DNS"),
        peer_endpoint_allowed_ips=config.get("Peers", "peer_endpoint_allowed_ips"),
        peer_mtu=config.get("Peers", "peer_mtu"),
        peer_keepalive=config.get("Peers", "peer_keep_alive"),
        peer_remote_endpoint=config.get("Peers", "remote_endpoint"),
    )


# Turn on / off a configuration
@app.route("/switch/<interface_name>", methods=["GET"])
def switch(interface_name):
    """
    On/off the wireguard interface.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: redirects
    """

    try:
        wg.switch_interface(interface_name, g.WG_CONF_PATH)
    except subprocess.CalledProcessError as exc:
        session["switch_msg"] = exc.output.strip().decode("utf-8")
        return redirect("/")
    return redirect(request.referrer)


@app.route("/update_acct", methods=["POST"])
def update_acct():
    """
    Change dashboard username
    @return: Redirect
    """

    if len(request.form["username"]) == 0:
        session["message"] = "Username cannot be empty."
        session["message_status"] = "danger"
        return redirect(url_for("settings"))
    config = g.conf
    config.set("Account", "username", request.form["username"])
    try:
        util.write_dashboard_conf(config, DASHBOARD_CONF_FILE)
        config.clear()
        session["message"] = "Username updated successfully!"
        session["message_status"] = "success"
        session["username"] = request.form["username"]
        return redirect(url_for("settings"))
    except Exception:
        session["message"] = "Username update failed."
        session["message_status"] = "danger"
        config.clear()
        return redirect(url_for("settings"))


# Update peer default setting
@app.route("/update_peer_default_config", methods=["POST"])
def update_peer_default_config():
    """
    Update new peers default setting
    @return: None
    """

    config = g.conf
    if (
        not (request.form["peer_endpoint_allowed_ips"])
        or not (request.form["peer_global_DNS"])
        or not (request.form["peer_remote_endpoint"])
    ):
        session["message"] = "Please fill in all required boxes."
        session["message_status"] = "danger"
        config.clear()
        return redirect(url_for("settings"))
    # Check DNS Format
    dns_addresses = request.form["peer_global_DNS"]
    if not util.check_DNS(dns_addresses):
        session["message"] = "Peer DNS Format Incorrect."
        session["message_status"] = "danger"
        config.clear()
        return redirect(url_for("settings"))
    dns_addresses = dns_addresses.replace(" ", "").split(",")
    dns_addresses = ",".join(dns_addresses)
    # Check Endpoint Allowed IPs
    ip = request.form["peer_endpoint_allowed_ips"]
    if not util.check_Allowed_IPs(ip):
        session["message"] = (
            "Peer Endpoint Allowed IPs Format Incorrect. "
            "Example: 192.168.1.1/32 or 192.168.1.1/32,192.168.1.2/32"
        )
        session["message_status"] = "danger"
        config.clear()
        return redirect(url_for("settings"))
    # Check MTU Format
    if not len(request.form["peer_mtu"]) > 0 or not request.form["peer_mtu"].isdigit():
        session["message"] = "MTU format is incorrect."
        session["message_status"] = "danger"
        config.clear()
        return redirect(url_for("settings"))
    # Check keepalive Format
    if (
        not len(request.form["peer_keep_alive"]) > 0
        or not request.form["peer_keep_alive"].isdigit()
    ):
        session["message"] = "Persistent keepalive format is incorrect."
        session["message_status"] = "danger"
        config.clear()
        return redirect(url_for("settings"))
    # Check peer remote endpoint
    if not util.check_remote_endpoint(request.form["peer_remote_endpoint"]):
        session["message"] = (
            "Peer Remote Endpoint format is incorrect. It can only be a valid "
            "IP address or valid domain (without http:// or https://). "
        )
        session["message_status"] = "danger"
        config.clear()
        return redirect(url_for("settings"))
    config.set("Peers", "remote_endpoint", request.form["peer_remote_endpoint"])
    config.set("Peers", "peer_keep_alive", request.form["peer_keep_alive"])
    config.set("Peers", "peer_mtu", request.form["peer_mtu"])
    config.set(
        "Peers", "peer_endpoint_allowed_ips", ",".join(util.clean_IP_with_range(ip))
    )
    config.set("Peers", "peer_global_DNS", dns_addresses)
    try:
        util.write_dashboard_conf(config, DASHBOARD_CONF_FILE)
        session["message"] = "Peer Default Settings update successfully!"
        session["message_status"] = "success"
        config.clear()
        return redirect(url_for("settings"))
    except Exception:
        session["message"] = "Peer Default Settings update failed."
        session["message_status"] = "danger"
        config.clear()
        return redirect(url_for("settings"))


# Update dashboard password
@app.route("/update_pwd", methods=["POST"])
def update_pwd():
    """
    Update dashboard password
    @return: Redirect
    """

    config = g.conf
    if hashlib.sha256(request.form["currentpass"].encode()).hexdigest() == config.get(
        "Account", "password"
    ):
        if (
            hashlib.sha256(request.form["newpass"].encode()).hexdigest()
            == hashlib.sha256(request.form["repnewpass"].encode()).hexdigest()
        ):
            config.set(
                "Account",
                "password",
                hashlib.sha256(request.form["repnewpass"].encode()).hexdigest(),
            )
            try:
                util.write_dashboard_conf(config, DASHBOARD_CONF_FILE)
                session["message"] = "Password updated successfully!"
                session["message_status"] = "success"
                config.clear()
                return redirect(url_for("settings"))
            except Exception:
                session["message"] = "Password update failed"
                session["message_status"] = "danger"
                config.clear()
                return redirect(url_for("settings"))
        else:
            session["message"] = "Your New Password does not match."
            session["message_status"] = "danger"
            config.clear()
            return redirect(url_for("settings"))
    else:
        session["message"] = "Your Password does not match."
        session["message_status"] = "danger"
        config.clear()
        return redirect(url_for("settings"))


@app.route("/update_app_ip_port", methods=["POST"])
def update_app_ip_port():
    """
    Update dashboard ip and port
    @return: None
    """

    config = g.conf
    config.set("Server", "app_ip", request.form["app_ip"])
    config.set("Server", "app_port", request.form["app_port"])
    util.write_dashboard_conf(config, DASHBOARD_CONF_FILE)
    config.clear()
    subprocess.Popen("bash wgd.sh restart", shell=True)
    return ""


# Update WireGuard configuration file path
@app.route("/update_wg_conf_path", methods=["POST"])
def update_wg_conf_path():
    """
    Update configuration path
    @return: None
    """

    config = g.conf
    config.set("Server", "wg_conf_path", request.form["wg_conf_path"])
    util.write_dashboard_conf(config, DASHBOARD_CONF_FILE)
    config.clear()
    session["message"] = "WireGuard Configuration Path updated successfully!"
    session["message_status"] = "success"
    subprocess.Popen("bash wgd.sh restart", shell=True)


# Configuration Page
@app.route("/configuration/<interface_name>", methods=["GET"])
def configuration(interface_name):
    """
    Show wireguard interface view.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Template
    """

    config = g.conf
    conf_data = {
        "name": interface_name,
        "status": wg.get_interface_status(interface_name),
        "checked": "",
    }
    if conf_data["status"] == "stopped":
        conf_data["checked"] = "nope"
    else:
        conf_data["checked"] = "checked"
    config_list = util.get_conf_list(WG_CONF_PATH)
    if interface_name not in [conf["conf"] for conf in config_list]:
        return render_template("index.html", conf=util.get_conf_list(WG_CONF_PATH))

    refresh_interval = int(config.get("Server", "dashboard_refresh_interval"))
    dns_address = config.get("Peers", "peer_global_DNS")
    allowed_ips = config.get("Peers", "peer_endpoint_allowed_ips")
    peer_mtu = config.get("Peers", "peer_MTU")
    peer_keep_alive = config.get("Peers", "peer_keep_alive")
    config.clear()
    return render_template(
        "configuration.html",
        conf=util.get_conf_list(WG_CONF_PATH),
        conf_data=conf_data,
        dashboard_refresh_interval=refresh_interval,
        DNS=dns_address,
        endpoint_allowed_ips=allowed_ips,
        title=interface_name,
        mtu=peer_mtu,
        keep_alive=peer_keep_alive,
    )


"""
Dashboard Tools Related
"""


# Get all IP for ping
@app.route("/get_ping_ip", methods=["POST"])
def get_ping_ip():
    # TODO: convert return to json object

    """
    Get ips for network testing.
    @return: HTML containing a list of IPs
    """

    config = request.form["config"]
    peers = g.cur.execute(
        "SELECT id, name, allowed_ips, endpoint FROM " + config
    ).fetchall()
    html = ""
    for i in peers:
        html += '<optgroup label="' + i[1] + " - " + i[0] + '">'
        allowed_ips = str(i[2]).split(",")
        for k in allowed_ips:
            k = k.split("/")
            if len(k) == 2:
                html += "<option value=" + k[0] + ">" + k[0] + "</option>"
        endpoint = str(i[3]).split(":")
        if len(endpoint) == 2:
            html += "<option value=" + endpoint[0] + ">" + endpoint[0] + "</option>"
        html += "</optgroup>"
    return html


# Ping IP
@app.route("/ping_ip", methods=["POST"])
def ping_ip():
    """
    Execute ping command.
    @return: Return text with result
    @rtype: str
    """

    try:
        result = ping(
            "" + request.form["ip"] + "",
            count=int(request.form["count"]),
            privileged=True,
            source=None,
        )
        returnjson = {
            "address": result.address,
            "is_alive": result.is_alive,
            "min_rtt": result.min_rtt,
            "avg_rtt": result.avg_rtt,
            "max_rtt": result.max_rtt,
            "package_sent": result.packets_sent,
            "package_received": result.packets_received,
            "package_loss": result.packet_loss,
        }
        if returnjson["package_loss"] == 1.0:
            returnjson["package_loss"] = returnjson["package_sent"]
        return jsonify(returnjson)
    except Exception:
        return "Error"


# Traceroute IP
@app.route("/traceroute_ip", methods=["POST"])
def traceroute_ip():
    """
    Execute ping traceroute command.

    @return: Return text with result
    @rtype: str
    """

    try:
        result = traceroute(
            "" + request.form["ip"] + "", first_hop=1, max_hops=30, count=1, fast=True
        )
        returnjson = []
        last_distance = 0
        for hop in result:
            if last_distance + 1 != hop.distance:
                returnjson.append(
                    {"hop": "*", "ip": "*", "avg_rtt": "", "min_rtt": "", "max_rtt": ""}
                )
            returnjson.append(
                {
                    "hop": hop.distance,
                    "ip": hop.address,
                    "avg_rtt": hop.avg_rtt,
                    "min_rtt": hop.min_rtt,
                    "max_rtt": hop.max_rtt,
                }
            )
            last_distance = hop.distance
        return jsonify(returnjson)
    except Exception:
        return "Error"


"""
Dashboard Initialization
"""


def read_and_update_config_file():
    """
    Create dashboard default configuration.
    """

    # Set Default INI File
    if not os.path.isfile(DASHBOARD_CONF_FILE):
        open(DASHBOARD_CONF_FILE, "w+").close()
    config = util.read_dashboard_conf(DASHBOARD_CONF_FILE)
    # Default dashboard account setting
    if "Account" not in config:
        config["Account"] = {}
    if "username" not in config["Account"]:
        config["Account"]["username"] = "admin"
    if "password" not in config["Account"]:
        config["Account"][
            "password"
        ] = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
    # Default dashboard server setting
    if "Server" not in config:
        config["Server"] = {}
    if "wg_conf_path" not in config["Server"]:
        config["Server"]["wg_conf_path"] = "/etc/wireguard"
    if "app_ip" not in config["Server"]:
        config["Server"]["app_ip"] = "0.0.0.0"
    if "app_port" not in config["Server"]:
        config["Server"]["app_port"] = "10086"
    if "auth_req" not in config["Server"]:
        config["Server"]["auth_req"] = "true"
    if (
        "version" not in config["Server"]
        or config["Server"]["version"] != DASHBOARD_VERSION
    ):
        config["Server"]["version"] = DASHBOARD_VERSION
    if "dashboard_refresh_interval" not in config["Server"]:
        config["Server"]["dashboard_refresh_interval"] = "60000"
    if "dashboard_sort" not in config["Server"]:
        config["Server"]["dashboard_sort"] = "status"
    # Default dashboard peers setting
    if "Peers" not in config:
        config["Peers"] = {}
    if "peer_global_DNS" not in config["Peers"]:
        config["Peers"]["peer_global_DNS"] = "1.1.1.1"
    if "peer_endpoint_allowed_ips" not in config["Peers"]:
        config["Peers"]["peer_endpoint_allowed_ips"] = "0.0.0.0/0"
    if "peer_display_mode" not in config["Peers"]:
        config["Peers"]["peer_display_mode"] = "grid"
    if "remote_endpoint" not in config["Peers"]:
        config["Peers"]["remote_endpoint"] = ifcfg.default_interface()["inet"]
    if "peer_MTU" not in config["Peers"]:
        config["Peers"]["peer_MTU"] = "1420"
    if "peer_keep_alive" not in config["Peers"]:
        config["Peers"]["peer_keep_alive"] = "21"
    util.write_dashboard_conf(config, DASHBOARD_CONF_FILE)
    return config


def check_update(config):
    """
    Dashboard check update

    @return: Retunt text with result
    @rtype: str
    """
    try:
        data = urllib.request.urlopen(
            "https://api.github.com/repos/donaldzou/WGDashboard/releases"
        ).read()
        output = json.loads(data)
        release = []
        for i in output:
            if not i["prerelease"]:
                release.append(i)
        if config.get("Server", "version") == release[0]["tag_name"]:
            result = "false"
        else:
            result = "true"

        return result
    except urllib.error.HTTPError:
        return "false"


"""
Configure DashBoard before start web-server
"""


def run_dashboard():
    global UPDATE
    config = util.read_dashboard_conf(DASHBOARD_CONF_FILE)
    UPDATE = check_update(config)
    # global app_ip
    app_ip = config.get("Server", "app_ip")
    # global app_port
    app_port = config.get("Server", "app_port")
    global WG_CONF_PATH
    WG_CONF_PATH = config.get("Server", "wg_conf_path")
    config.clear()
    app.run(host=app_ip, debug=False, port=app_port)
    return app


"""
Get host and port for web-server
"""


def get_host_bind():
    config = util.read_dashboard_conf(DASHBOARD_CONF_FILE)
    app_ip = config.get("Server", "app_ip")
    app_port = config.get("Server", "app_port")
    return app_ip, app_port


if __name__ == "__main__":
    # UPDATE = check_update()
    # config = util.read_dashboard_conf(DASHBOARD_CONF_FILE)
    # # global app_ip
    # app_ip = config.get("Server", "app_ip")
    # # global app_port
    # app_port = config.get("Server", "app_port")
    # WG_CONF_PATH = config.get("Server", "wg_conf_path")
    # config.clear()
    # app.run(host=app_ip, debug=False, port=app_port)
    run_dashboard()
