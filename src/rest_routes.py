import subprocess
import os
from flask import request, redirect, session, jsonify, g, render_template
from __main__ import app
from datetime import datetime
import urllib.parse
import urllib.request
import urllib.error

# Import local modules
import db, wg, util


@app.route("/update_dashboard_sort", methods=["POST"])
def update_dashbaord_sort():
    """
    Update configuration sorting
    @return: Boolean
    """

    config = g.conf
    data = request.get_json()
    sort_tag = ["name", "status", "allowed_ips"]
    if data["sort"] in sort_tag:
        config.set("Server", "dashboard_sort", data["sort"])
    else:
        config.set("Server", "dashboard_sort", "status")
    util.write_dashboard_conf(config, g.DASHBOARD_CONF_FILE)
    config.clear()
    return "true"


# Update configuration refresh interval
@app.route("/update_dashboard_refresh_interval", methods=["POST"])
def update_dashboard_refresh_interval():
    """
    Change the refresh time.
    @return: Return text with result
    @rtype: str
    """

    preset_interval = ["5000", "10000", "30000", "60000"]
    if request.form["interval"] in preset_interval:
        config = g.conf
        config.set(
            "Server", "dashboard_refresh_interval", str(request.form["interval"])
        )
        util.write_dashboard_conf(config, g.DASHBOARD_CONF_FILE)
        config.clear()
        return "true"
    else:
        return "false"


@app.route("/qrcode/<interface_name>", methods=["GET"])
def generate_qrcode(interface_name):
    """
    Generate QRCode
    @param interface_name: Configuration Name
    @return: Template containing QRcode img
    """

    peer_id = request.args.get("id")
    get_peer = g.cur.execute(
        "SELECT private_key, allowed_ips, DNS, mtu, endpoint_allowed_ips, keepalive, preshared_key FROM "
        + interface_name
        + " WHERE id = ?",
        (peer_id,),
    ).fetchall()
    config = g.conf
    if len(get_peer) == 1:
        peer = get_peer[0]
        if peer[0] != "":
            public_key = wg.get_interface_public_key(interface_name, g.WG_CONF_PATH)
            listen_port = wg.get_interface_listen_port(interface_name, g.WG_CONF_PATH)
            endpoint = config.get("Peers", "remote_endpoint") + ":" + listen_port
            private_key = peer[0]
            allowed_ips = peer[1]
            dns_addresses = peer[2]
            mtu_value = peer[3]
            endpoint_allowed_ips = peer[4]
            keepalive = peer[5]
            preshared_key = peer[6]

            result = (
                "[Interface]\nPrivateKey = "
                + private_key
                + "\nAddress = "
                + allowed_ips
                + "\nMTU = "
                + str(mtu_value)
                + "\nDNS = "
                + dns_addresses
                + "\n\n[Peer]\nPublicKey = "
                + public_key
                + "\nAllowedIPs = "
                + endpoint_allowed_ips
                + "\nPersistentKeepalive = "
                + str(keepalive)
                + "\nEndpoint = "
                + endpoint
            )
            if preshared_key != "":
                result += "\nPresharedKey = " + preshared_key
            return render_template("qrcode.html", i=result)
    else:
        return redirect("/configuration/" + interface_name)


@app.route("/download_all/<interface_name>", methods=["GET"])
def download_all(interface_name):
    """
    Download all configuration
    @param interface_name: Configuration Name
    @return: JSON Object
    """

    get_peer = g.cur.execute(
        "SELECT private_key, allowed_ips, DNS, mtu, endpoint_allowed_ips, keepalive, preshared_key, name FROM "
        + interface_name
        + " WHERE private_key != ''"
    ).fetchall()
    config = g.conf
    data = []
    public_key = wg.get_interface_public_key(interface_name, g.WG_CONF_PATH)
    listen_port = wg.get_interface_listen_port(interface_name, g.WG_CONF_PATH)
    endpoint = config.get("Peers", "remote_endpoint") + ":" + listen_port
    for peer in get_peer:
        private_key = peer[0]
        allowed_ips = peer[1]
        dns_addresses = peer[2]
        mtu_value = peer[3]
        endpoint_allowed_ips = peer[4]
        keepalive = peer[5]
        preshared_key = peer[6]
        filename = peer[7]
        if len(filename) == 0:
            filename = "Untitled_Peer"
        else:
            filename = peer[7]
            # Clean filename
            illegal_filename = [
                ".",
                ",",
                "/",
                "?",
                "<",
                ">",
                "\\",
                ":",
                "*",
                "|" '"',
                "com1",
                "com2",
                "com3",
                "com4",
                "com5",
                "com6",
                "com7",
                "com8",
                "com9",
                "lpt1",
                "lpt2",
                "lpt3",
                "lpt4",
                "lpt5",
                "lpt6",
                "lpt7",
                "lpt8",
                "lpt9",
                "con",
                "nul",
                "prn",
            ]
            for i in illegal_filename:
                filename = filename.replace(i, "")
            if len(filename) == 0:
                filename = "Untitled_Peer"
            filename = "".join(filename.split(" "))
        filename = filename + "_" + interface_name
        psk = ""
        if preshared_key != "":
            psk = "\nPresharedKey = " + preshared_key

        return_data = (
            "[Interface]\nPrivateKey = "
            + private_key
            + "\nAddress = "
            + allowed_ips
            + "\nDNS = "
            + dns_addresses
            + "\nMTU = "
            + str(mtu_value)
            + "\n\n[Peer]\nPublicKey = "
            + public_key
            + "\nAllowedIPs = "
            + endpoint_allowed_ips
            + "\nEndpoint = "
            + endpoint
            + "\nPersistentKeepalive = "
            + str(keepalive)
            + psk
        )
        data.append({"filename": f"{filename}.conf", "content": return_data})
    return jsonify({"status": True, "peers": data, "filename": f"{interface_name}.zip"})


# Download configuration file
@app.route("/download/<interface_name>", methods=["GET"])
def download(interface_name):
    """
    Download one configuration
    @param interface_name: Configuration name
    @return: JSON object
    """

    peer_id = request.args.get("id")
    get_peer = g.cur.execute(
        "SELECT private_key, allowed_ips, DNS, mtu, endpoint_allowed_ips, keepalive, preshared_key, name FROM "
        + interface_name
        + " WHERE id = ?",
        (peer_id,),
    ).fetchall()
    config = g.conf
    if len(get_peer) == 1:
        peer = get_peer[0]
        if peer[0] != "":
            public_key = wg.get_interface_public_key(interface_name, g.WG_CONF_PATH)
            listen_port = wg.get_interface_listen_port(interface_name, g.WG_CONF_PATH)
            endpoint = config.get("Peers", "remote_endpoint") + ":" + listen_port
            private_key = peer[0]
            allowed_ips = peer[1]
            dns_addresses = peer[2]
            mtu_value = peer[3]
            endpoint_allowed_ips = peer[4]
            keepalive = peer[5]
            preshared_key = peer[6]
            filename = peer[7]
            if len(filename) == 0:
                filename = "Untitled_Peer"
            else:
                filename = peer[7]
                # Clean filename
                illegal_filename = [
                    ".",
                    ",",
                    "/",
                    "?",
                    "<",
                    ">",
                    "\\",
                    ":",
                    "*",
                    "|" '"',
                    "com1",
                    "com2",
                    "com3",
                    "com4",
                    "com5",
                    "com6",
                    "com7",
                    "com8",
                    "com9",
                    "lpt1",
                    "lpt2",
                    "lpt3",
                    "lpt4",
                    "lpt5",
                    "lpt6",
                    "lpt7",
                    "lpt8",
                    "lpt9",
                    "con",
                    "nul",
                    "prn",
                ]
                for i in illegal_filename:
                    filename = filename.replace(i, "")
                if len(filename) == 0:
                    filename = "Untitled_Peer"
                filename = "".join(filename.split(" "))
            filename = filename + "_" + interface_name
            psk = ""
            if preshared_key != "":
                psk = "\nPresharedKey = " + preshared_key

            return_data = (
                "[Interface]\nPrivateKey = "
                + private_key
                + "\nAddress = "
                + allowed_ips
                + "\nDNS = "
                + dns_addresses
                + "\nMTU = "
                + str(mtu_value)
                + "\n\n[Peer]\nPublicKey = "
                + public_key
                + "\nAllowedIPs = "
                + endpoint_allowed_ips
                + "\nEndpoint = "
                + endpoint
                + "\nPersistentKeepalive = "
                + str(keepalive)
                + psk
            )

            return jsonify(
                {"status": True, "filename": f"{filename}.conf", "content": return_data}
            )
    return jsonify({"status": False, "filename": "", "content": ""})


@app.route("/add_peer/<interface_name>", methods=["POST"])
def add_peer(interface_name):
    """
    Add Peers
    @param interface_name: configuration name
    @return: string
    """

    interface_name = interface_name
    data = request.get_json()
    public_key = data["public_key"]
    allowed_ips = data["allowed_ips"]
    endpoint_allowed_ips = data["endpoint_allowed_ips"]
    dns_addresses = data["DNS"]
    enable_preshared_key = data["enable_preshared_key"]
    preshared_key = data["preshared_key"]
    keys = wg.get_interface_peer_public_keys(interface_name)
    if (
        len(public_key) == 0
        or len(dns_addresses) == 0
        or len(allowed_ips) == 0
        or len(endpoint_allowed_ips) == 0
    ):
        return "Please fill in all required box."
    if not isinstance(keys, list):
        return interface_name + " is not running."
    if public_key in keys:
        return "Public key already exist."
    check_dup_ip = g.cur.execute(
        "SELECT COUNT(*) FROM "
        + interface_name
        + " WHERE allowed_ips LIKE '"
        + allowed_ips
        + "/%'",
    ).fetchone()
    if check_dup_ip[0] != 0:
        return "Allowed IP already taken by another peer."
    if not util.check_DNS(dns_addresses):
        return "DNS formate is incorrect. Example: 1.1.1.1"
    if not util.check_Allowed_IPs(endpoint_allowed_ips):
        return "Endpoint Allowed IPs format is incorrect."
    if len(data["MTU"]) == 0 or not data["MTU"].isdigit():
        return "MTU format is not correct."
    if len(data["keep_alive"]) == 0 or not data["keep_alive"].isdigit():
        return "Persistent Keepalive format is not correct."
    try:
        if enable_preshared_key:
            now = str(datetime.now().strftime("%m%d%Y%H%M%S"))
            f_name = now + "_tmp_psk.txt"
            f = open(f_name, "w+")
            f.write(preshared_key)
            f.close()
            wg.set_peer_options(interface_name, public_key, allowed_ips, f_name)
            os.remove(f_name)
        elif not enable_preshared_key:
            wg.set_peer_options(interface_name, public_key, allowed_ips)

        wg.quick_save_interface_config(interface_name, g.WG_CONF_PATH)
        util.wg_peer_data_to_db(interface_name, g.WG_CONF_PATH, g.DASHBOARD_CONF_FILE)
        data = {
            "id": public_key,
            "name": data["name"],
            "private_key": data["private_key"],
            "DNS": data["DNS"],
            "endpoint_allowed_ips": endpoint_allowed_ips,
        }
        db.update_peer(interface_name, data)
        return "true"
    except subprocess.CalledProcessError as exc:
        return exc.output.strip()


@app.route("/save_peer_setting/<interface_name>", methods=["POST"])
def save_peer_setting(interface_name):
    """
    Save peer configuration.

    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Return status of action and text with recommendations
    """

    data = request.get_json()
    id = data["id"]
    name = data["name"]
    private_key = data["private_key"]
    dns_addresses = data["DNS"]
    allowed_ips = data["allowed_ips"]
    endpoint_allowed_ips = data["endpoint_allowed_ips"]
    preshared_key = data["preshared_key"]
    db_peer = db.get_peer_by_id(interface_name, id)
    if db_peer:
        check_ip = util.check_repeat_allowed_ips(id, allowed_ips, interface_name)
        if not util.check_IP_with_range(endpoint_allowed_ips):
            return jsonify(
                {"status": "failed", "msg": "Endpoint Allowed IPs format is incorrect."}
            )
        if not util.check_DNS(dns_addresses):
            return jsonify({"status": "failed", "msg": "DNS format is incorrect."})
        if len(data["MTU"]) == 0 or not data["MTU"].isdigit():
            return jsonify({"status": "failed", "msg": "MTU format is not correct."})
        if len(data["keep_alive"]) == 0 or not data["keep_alive"].isdigit():
            return jsonify(
                {
                    "status": "failed",
                    "msg": "Persistent Keepalive format is not correct.",
                }
            )
        if private_key != "":
            check_key = util.f_check_key_match(private_key, id, interface_name)
            if check_key["status"] == "failed":
                return jsonify(check_key)
        if check_ip["status"] == "failed":
            return jsonify(check_ip)
        try:
            tmp_psk = open("tmp_edit_psk.txt", "w+")
            tmp_psk.write(preshared_key)
            tmp_psk.close()
            change_psk = subprocess.check_output(
                f"wg set {interface_name} peer {id} preshared-key tmp_edit_psk.txt",
                shell=True,
                stderr=subprocess.STDOUT,
            )
            if change_psk.decode("UTF-8") != "":
                return jsonify({"status": "failed", "msg": change_psk.decode("UTF-8")})
            if allowed_ips == "":
                allowed_ips = '""'
            allowed_ips = allowed_ips.replace(" ", "")
            change_ip = subprocess.check_output(
                f"wg set {interface_name} peer {id} allowed-ips {allowed_ips}",
                shell=True,
                stderr=subprocess.STDOUT,
            )
            wg.quick_save_interface_config(interface_name, g.WG_CONF_PATH)
            if change_ip.decode("UTF-8") != "":
                return jsonify({"status": "failed", "msg": change_ip.decode("UTF-8")})

            db.update_peer(
                interface_name,
                {
                    "name": name,
                    "private_key": private_key,
                    "DNS": dns_addresses,
                    "endpoint_allowed_ips": endpoint_allowed_ips,
                    "mtu": data["MTU"],
                    "keepalive": data["keep_alive"],
                    "preshared_key": preshared_key,
                    "id": id,
                },
            )
            return jsonify({"status": "success", "msg": ""})
        except subprocess.CalledProcessError as exc:
            return jsonify(
                {"status": "failed", "msg": str(exc.output.decode("UTF-8").strip())}
            )
    else:
        return jsonify({"status": "failed", "msg": "This peer does not exist."})


# Get peer settings
@app.route("/get_peer_data/<interface_name>", methods=["POST"])
def get_peer_data(interface_name):
    """
    Get peer settings.

    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Return settings of peer
    """

    interface_name = interface_name

    data = request.get_json()
    peer_id = data["id"]
    db_peer = dict(db.get_peer_by_id(interface_name, peer_id))
    db_peer = util.adapt_for_rest(db_peer)
    return jsonify(db_peer)


# Return available IPs
@app.route("/available_ips/<interface_name>", methods=["GET"])
def available_ips(interface_name):

    return jsonify(util.f_available_ips(interface_name, g.WG_CONF_PATH))


# Check if both key match
@app.route("/check_key_match/<interface_name>", methods=["POST"])
def check_key_match(interface_name):
    """
    Check key matches
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Return dictionary with status
    """

    data = request.get_json()
    private_key = data["private_key"]
    public_key = data["public_key"]
    return jsonify(util.f_check_key_match(private_key, public_key, interface_name))


@app.route("/switch_display_mode/<mode>", methods=["GET"])
def switch_display_mode(mode):
    """
    Change display view style.

    @param mode: Mode name
    @type mode: str
    @return: Return text with result
    @rtype: str
    """

    if mode in ["list", "grid"]:
        config = g.conf
        config.set("Peers", "peer_display_mode", mode)
        util.write_dashboard_conf(config, g.DASHBOARD_CONF_FILE)
        config.clear()
        return "true"
    return "false"


# Get configuration details
@app.route("/get_config/<interface_name>", methods=["GET"])
def get_conf(interface_name):
    """
    Get configuration setting of wireguard interface.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: TODO
    """

    config_interface = wg.read_interface_section_from_config_file(
        interface_name, g.WG_CONF_PATH
    )
    search = request.args.get("search")
    if len(search) == 0:
        search = ""
    search = urllib.parse.unquote(search)
    config = g.conf
    sort = config.get("Server", "dashboard_sort")
    peer_display_mode = config.get("Peers", "peer_display_mode")
    wg_ip = config.get("Peers", "remote_endpoint")
    if "Address" not in config_interface:
        conf_address = "N/A"
    else:
        conf_address = config_interface["Address"]
    conf_data = {
        "peer_data": util.update_db_and_get_peers(
            interface_name, search, sort, g.WG_CONF_PATH, g.DASHBOARD_CONF_FILE
        ),
        "name": interface_name,
        "status": wg.get_interface_status(interface_name),
        "total_data_usage": wg.get_interface_total_net_stats(interface_name),
        "public_key": wg.get_interface_public_key(interface_name, g.WG_CONF_PATH),
        "listen_port": wg.get_interface_listen_port(interface_name, g.WG_CONF_PATH),
        "running_peer": wg.get_interface_running_peer_count(interface_name),
        "conf_address": conf_address,
        "wg_ip": wg_ip,
        "sort_tag": sort,
        "dashboard_refresh_interval": int(
            config.get("Server", "dashboard_refresh_interval")
        ),
        "peer_display_mode": peer_display_mode,
    }
    if conf_data["status"] == "stopped":
        conf_data["checked"] = "nope"
    else:
        conf_data["checked"] = "checked"
    config.clear()
    return jsonify(conf_data)


@app.route("/remove_peer/<interface_name>", methods=["POST"])
def remove_peer(interface_name):
    """
    Remove peer.
    @param interface_name: Name of WG interface
    @type interface_name: str
    @return: Return result of action or recommendations
    @rtype: str
    """

    interface_name = interface_name
    if wg.get_interface_status(interface_name) == "stopped":
        return "Your need to turn on " + interface_name + " first."
    data = request.get_json()
    delete_keys = data["peer_ids"]
    keys = wg.get_interface_peer_public_keys(interface_name)
    if not isinstance(keys, list):
        return interface_name + " is not running."
    else:
        for id in delete_keys:
            if id not in keys:
                return "This key does not exist"
            db.delete_peer(interface_name, id)
            try:
                wg.remove_peer_from_interface(interface_name, id)
                wg.quick_save_interface_config(interface_name, g.WG_CONF_PATH)
            except subprocess.CalledProcessError as exc:
                return exc.output.strip()
            return "true"


@app.route("/add_peer_bulk/<interface_name>", methods=["POST"])
def add_peer_bulk(interface_name):
    """
    Add peers by bulk
    @param interface_name: Configuration Name
    @return: String
    """

    data = request.get_json()
    keys = data["keys"]
    endpoint_allowed_ips = data["endpoint_allowed_ips"]
    dns_addresses = data["DNS"]
    enable_preshared_key = data["enable_preshared_key"]
    amount = data["amount"]
    config_interface = wg.read_interface_section_from_config_file(
        interface_name, g.WG_CONF_PATH
    )
    if "Address" not in config_interface:
        return "Configuration must have an IP address."
    if not amount.isdigit() or int(amount) < 1:
        return "Amount must be integer larger than 0"
    amount = int(amount)
    if not util.check_DNS(dns_addresses):
        return "DNS formate is incorrect. Example: 1.1.1.1"
    if not util.check_Allowed_IPs(endpoint_allowed_ips):
        return "Endpoint Allowed IPs format is incorrect."
    if len(data["MTU"]) == 0 or not data["MTU"].isdigit():
        return "MTU format is not correct."
    if len(data["keep_alive"]) == 0 or not data["keep_alive"].isdigit():
        return "Persistent Keepalive format is not correct."
    ips = util.f_available_ips(interface_name)
    if amount > len(ips):
        return f"Cannot create more than {len(ips)} peers."
    wg_command = ["wg", "set", interface_name]
    sql_command = []
    for i in range(amount):
        keys[i][
            "name"
        ] = f"{interface_name}_{datetime.now().strftime('%m%d%Y%H%M%S')}_Peer_#_{(i + 1)}"
        wg_command.append("peer")
        wg_command.append(keys[i]["publicKey"])
        keys[i]["allowed_ips"] = ips.pop(0)
        if enable_preshared_key:
            keys[i]["psk_file"] = f"{keys[i]['name']}.txt"
            f = open(keys[i]["psk_file"], "w+")
            f.write(keys[i]["presharedKey"])
            f.close()
            wg_command.append("preshared-key")
            wg_command.append(keys[i]["psk_file"])
        else:
            keys[i]["psk_file"] = ""
        wg_command.append("allowed-ips")
        wg_command.append(keys[i]["allowed_ips"])
        update = [
            "UPDATE ",
            interface_name,
            " SET name = '",
            keys[i]["name"],
            "', private_key = '",
            keys[i]["privateKey"],
            "', DNS = '",
            dns_addresses,
            "', endpoint_allowed_ips = '",
            endpoint_allowed_ips,
            "' WHERE id = '",
            keys[i]["publicKey"],
            "'",
        ]
        sql_command.append(update)
    try:
        status = subprocess.check_output(
            " ".join(wg_command), shell=True, stderr=subprocess.STDOUT
        )
        wg.quick_save_interface_config(interface_name, g.WG_CONF_PATH)
        util.wg_peer_data_to_db(interface_name, g.WG_CONF_PATH, g.DASHBOARD_CONF_FILE)
        if enable_preshared_key:
            for i in keys:
                os.remove(i["psk_file"])
        for i in range(len(sql_command)):
            sql_command[i] = "".join(sql_command[i])
        g.cur.executescript("; ".join(sql_command))
        return "true"
    except subprocess.CalledProcessError as exc:
        return exc.output.strip()
