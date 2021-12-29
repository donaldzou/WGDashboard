"""
< WGDashboard > - by Donald Zou [https://github.com/donaldzou]
Under Apache-2.0 License
"""

import configparser
import hashlib
import ipaddress
import json
# Python Built-in Library
import os
import secrets
import subprocess
import threading
import time
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from operator import itemgetter

# PIP installed library
import ifcfg
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_qrcode import QRcode
from icmplib import ping, traceroute
from tinydb import TinyDB, Query

# Import other python files
from util import regex_match, check_DNS, check_Allowed_IPs, check_remote_endpoint,\
    check_IP_with_range, clean_IP_with_range

# Dashboard Version
DASHBOARD_VERSION = 'v3.0'
# Dashboard Config Name
configuration_path = os.getenv('CONFIGURATION_PATH', '.')
db_path = os.path.join(configuration_path, 'db')
if not os.path.isdir(db_path):
    os.mkdir(db_path)
DASHBOARD_CONF = os.path.join(configuration_path, 'wg-dashboard.ini')
# Upgrade Required
UPDATE = None
# Flask App Configuration
app = Flask("WGDashboard")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 5206928
app.secret_key = secrets.token_urlsafe(16)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Enable QR Code Generator
QRcode(app)

# TODO: Testing semaphore on reading/writing database
sem = threading.RLock()


# Read / Write Dashboard Config File
def get_dashboard_conf():
    """
    Dashboard Configuration Related
    """

    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    return config


def set_dashboard_conf(config):
    with open(DASHBOARD_CONF, "w", encoding='utf-8') as conf_object:
        config.write(conf_object)


# Get all keys from a configuration
def get_conf_peer_key(config_name):
    """
    Configuration Related
    """

    try:
        peer_key = subprocess.run(f"wg show {config_name} peers",
                                  check=True, shell=True, capture_output=True).stdout
        peer_key = peer_key.decode("UTF-8").split()
        return peer_key
    except subprocess.CalledProcessError:
        return config_name + " is not running."


# Get numbers of connected peer of a configuration
def get_conf_running_peer_number(config_name):
    running = 0
    # Get latest handshakes
    try:
        data_usage = subprocess.run(f"wg show {config_name} latest-handshakes",
                                    check=True, shell=True, capture_output=True).stdout
    except subprocess.CalledProcessError:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    now = datetime.now()
    time_delta = timedelta(minutes=2)
    for _ in range(int(len(data_usage) / 2)):
        minus = now - datetime.fromtimestamp(int(data_usage[count + 1]))
        if minus < time_delta:
            running += 1
        count += 2
    return running


# Read [Interface] section from configuration file
def read_conf_file_interface(config_name):
    conf_location = wg_conf_path + "/" + config_name + ".conf"
    with open(conf_location, 'r', encoding='utf-8') as file_object:
        file = file_object.read().split("\n")
        data = {}
        for i in file:
            if not regex_match("#(.*)", i):
                if len(i) > 0:
                    if i != "[Interface]":
                        tmp = re.split(r'\s*=\s*', i, 1)
                        if len(tmp) == 2:
                            data[tmp[0]] = tmp[1]
    return data


# Read the whole configuration file
def read_conf_file(config_name):
    # Read Configuration File Start
    conf_location = wg_conf_path + "/" + config_name + ".conf"
    with open(conf_location, 'r', encoding='utf-8') as file_object:
        file = file_object.read().split("\n")
    conf_peer_data = {
        "Interface": {},
        "Peers": []
    }
    peers_start = 0
    for i in file:
        if not regex_match("#(.*)", i):
            if i == "[Peer]":
                peers_start = i
                break

            if len(i) > 0:
                if i != "[Interface]":
                    tmp = re.split(r'\s*=\s*', i, 1)
                    if len(tmp) == 2:
                        conf_peer_data['Interface'][tmp[0]] = tmp[1]
    conf_peers = file[peers_start:]
    peer = -1
    for i in conf_peers:
        if not regex_match("#(.*)", i):
            if i == "[Peer]":
                peer += 1
                conf_peer_data["Peers"].append({})
            elif peer > -1:
                if len(i) > 0:
                    tmp = re.split(r'\s*=\s*', i, 1)
                    if len(tmp) == 2:
                        conf_peer_data["Peers"][peer][tmp[0]] = tmp[1]

    # Read Configuration File End
    return conf_peer_data


# Get latest handshake from all peers of a configuration
def get_latest_handshake(config_name, db, peers):
    # Get latest handshakes
    try:
        data_usage = subprocess.run(f"wg show {config_name} latest-handshakes",
                                    check=True, shell=True, capture_output=True).stdout
    except subprocess.CalledProcessError:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    now = datetime.now()
    time_delta = timedelta(minutes=2)
    for _ in range(int(len(data_usage) / 2)):
        minus = now - datetime.fromtimestamp(int(data_usage[count + 1]))
        if minus < time_delta:
            status = "running"
        else:
            status = "stopped"
        if int(data_usage[count + 1]) > 0:
            db.update({"latest_handshake": str(minus).split(".", maxsplit=1)[0], "status": status},
                      peers.id == data_usage[count])
        else:
            db.update({"latest_handshake": "(None)", "status": status}, peers.id == data_usage[count])
        count += 2

    return None


# Get transfer from all peers of a configuration
def get_transfer(config_name, db, peers):
    # Get transfer
    try:
        data_usage = subprocess.run(f"wg show {config_name} transfer",
                                    check=True, shell=True, capture_output=True).stdout
    except subprocess.CalledProcessError:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    for _ in range(int(len(data_usage) / 3)):
        cur_i = db.search(peers.id == data_usage[count])
        total_sent = cur_i[0]['total_sent']
        total_receive = cur_i[0]['total_receive']
        traffic = cur_i[0]['traffic']
        cur_total_sent = round(int(data_usage[count + 2]) / (1024 ** 3), 4)
        cur_total_receive = round(int(data_usage[count + 1]) / (1024 ** 3), 4)
        if cur_i[0]["status"] == "running":
            if total_sent <= cur_total_sent and total_receive <= cur_total_receive:
                total_sent = cur_total_sent
                total_receive = cur_total_receive
            else:
                now = datetime.now()
                ctime = now.strftime("%d/%m/%Y %H:%M:%S")
                traffic.append(
                    {"time": ctime, "total_receive": round(total_receive, 4), "total_sent": round(total_sent, 4),
                     "total_data": round(total_receive + total_sent, 4)})
                total_sent = 0
                total_receive = 0
                db.update({"traffic": traffic}, peers.id == data_usage[count])
            db.update({"total_receive": round(total_receive, 4),
                       "total_sent": round(total_sent, 4),
                       "total_data": round(total_receive + total_sent, 4)}, peers.id == data_usage[count])

        count += 3

    return None


# Get endpoint from all peers of a configuration
def get_endpoint(config_name, db, peers):
    # Get endpoint
    try:
        data_usage = subprocess.run(f"wg show {config_name} endpoints",
                                    check=True, shell=True, capture_output=True).stdout
    except subprocess.CalledProcessError:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    for _ in range(int(len(data_usage) / 2)):
        db.update({"endpoint": data_usage[count + 1]}, peers.id == data_usage[count])
        count += 2

    return None


# Get allowed ips from all peers of a configuration
def get_allowed_ip(db, peers, conf_peer_data):
    # Get allowed ip
    for i in conf_peer_data["Peers"]:
        db.update({"allowed_ip": i.get('AllowedIPs', '(None)')}, peers.id == i["PublicKey"])


# Look for new peers from WireGuard
def get_all_peers_data(config_name):
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config_name + '.json'))
    peers = Query()
    conf_peer_data = read_conf_file(config_name)
    config = get_dashboard_conf()
    for i in conf_peer_data['Peers']:
        search = db.search(peers.id == i['PublicKey'])
        if not search:
            new_data = {
                "id": i['PublicKey'],
                "private_key": "",
                "DNS": config.get("Peers", "peer_global_DNS"),
                "endpoint_allowed_ip": config.get("Peers", "peer_endpoint_allowed_ip"),
                "name": "",
                "total_receive": 0,
                "total_sent": 0,
                "total_data": 0,
                "endpoint": "N/A",
                "status": "stopped",
                "latest_handshake": "N/A",
                "allowed_ip": "N/A",
                "traffic": [],
                "mtu": config.get("Peers", "peer_mtu"),
                "keepalive": config.get("Peers", "peer_keep_alive"),
                "remote_endpoint": config.get("Peers", "remote_endpoint"),
                "preshared_key": ""
            }
            if "PresharedKey" in i.keys():
                new_data["preshared_key"] = i["PresharedKey"]
            db.insert(new_data)
        else:
            # Update database since V2.2
            update_db = {}
            # Required peer settings
            if "DNS" not in search[0]:
                update_db['DNS'] = config.get("Peers", "peer_global_DNS")
            if "endpoint_allowed_ip" not in search[0]:
                update_db['endpoint_allowed_ip'] = config.get("Peers", "peer_endpoint_allowed_ip")
            # Not required peers settings (Only for QR code)
            if "private_key" not in search[0]:
                update_db['private_key'] = ''
            if "mtu" not in search[0]:
                update_db['mtu'] = config.get("Peers", "peer_mtu")
            if "keepalive" not in search[0]:
                update_db['keepalive'] = config.get("Peers", "peer_keep_alive")
            if "remote_endpoint" not in search[0]:
                update_db['remote_endpoint'] = config.get("Peers","remote_endpoint")
            if "preshared_key" not in search[0]:
                if "PresharedKey" in i.keys():
                    update_db['preshared_key'] = i["PresharedKey"]
                else:
                    update_db['preshared_key'] = ""
            db.update(update_db, peers.id == i['PublicKey'])
    # Remove peers no longer exist in WireGuard configuration file
    db_key = list(map(lambda a: a['id'], db.all()))
    wg_key = list(map(lambda a: a['PublicKey'], conf_peer_data['Peers']))
    for i in db_key:
        if i not in wg_key:
            db.remove(peers.id == i)
    tic = time.perf_counter()
    get_latest_handshake(config_name, db, peers)
    get_transfer(config_name, db, peers)
    get_endpoint(config_name, db, peers)
    get_allowed_ip(db, peers, conf_peer_data)
    toc = time.perf_counter()
    print(f"Finish fetching data in {toc - tic:0.4f} seconds")
    db.close()
    try:
        sem.release()
    except RuntimeError as e:
        print("RuntimeError: cannot release un-acquired lock")


# Search for peers
def get_peers(config_name, search, sort_t):
    """
    Frontend Related Functions
    """

    get_all_peers_data(config_name)
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config_name + ".json"))
    peer = Query()
    if len(search) == 0:
        result = db.all()
    else:
        result = db.search(peer.name.matches('(.*)(' + re.escape(search) + ')(.*)'))
    if sort_t == "allowed_ip":
        result = sorted(result, key=lambda d: ipaddress.ip_network(d[sort_t].split(",")[0]))
    else:
        result = sorted(result, key=lambda d: d[sort_t])
    db.close()
    try:
        sem.release()
    except RuntimeError as e:
        print("RuntimeError: cannot release un-acquired lock")
    return result


# Get configuration public key
def get_conf_pub_key(config_name):
    conf = configparser.ConfigParser(strict=False)
    conf.read(wg_conf_path + "/" + config_name + ".conf")
    pri = conf.get("Interface", "PrivateKey")
    pub = subprocess.run(f"echo '{pri}' | wg pubkey", check=True, shell=True, capture_output=True).stdout
    conf.clear()
    return pub.decode().strip("\n")


# Get configuration listen port
def get_conf_listen_port(config_name):
    conf = configparser.ConfigParser(strict=False)
    conf.read(wg_conf_path + "/" + config_name + ".conf")
    port = ""
    try:
        port = conf.get("Interface", "ListenPort")
    except (configparser.NoSectionError, configparser.NoOptionError):
        if get_conf_status(config_name) == "running":
            port = subprocess.run(f"wg show {config_name} listen-port",
                                  check=True, shell=True, capture_output=True).stdout
            port = port.decode("UTF-8")
    conf.clear()
    return port


# Get configuration total data
def get_conf_total_data(config_name):
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config_name + ".json"))
    upload_total = 0
    download_total = 0
    for i in db.all():
        upload_total += i['total_sent']
        download_total += i['total_receive']
        for k in i['traffic']:
            upload_total += k['total_sent']
            download_total += k['total_receive']
    total = round(upload_total + download_total, 4)
    upload_total = round(upload_total, 4)
    download_total = round(download_total, 4)
    db.close()
    try:
        sem.release()
    except RuntimeError as e:
        print("RuntimeError: cannot release un-acquired lock")
    return [total, upload_total, download_total]


# Get configuration status
def get_conf_status(config_name):
    ifconfig = dict(ifcfg.interfaces().items())

    return "running" if config_name in ifconfig.keys() else "stopped"


# Get all configuration as a list
def get_conf_list():
    conf = []
    for i in os.listdir(wg_conf_path):
        if regex_match("^(.{1,}).(conf)$", i):
            i = i.replace('.conf', '')
            temp = {"conf": i, "status": get_conf_status(i), "public_key": get_conf_pub_key(i)}
            if temp['status'] == "running":
                temp['checked'] = 'checked'
            else:
                temp['checked'] = ""
            conf.append(temp)
    if len(conf) > 0:
        conf = sorted(conf, key=itemgetter('conf'))
    return conf


# Generate private key
def gen_private_key():
    gen = subprocess.check_output('wg genkey > private_key.txt && wg pubkey < private_key.txt > public_key.txt',
                                  shell=True)
    gen_psk = subprocess.check_output('wg genpsk', shell=True)
    preshare_key = gen_psk.decode("UTF-8").strip()
    with open('private_key.txt', encoding='utf-8') as file_object:
        private_key = file_object.readline().strip()
    with open('public_key.txt', encoding='utf-8') as file_object:
        public_key = file_object.readline().strip()
    data = {"private_key": private_key, "public_key": public_key, "preshared_key": preshare_key}
    private.close()
    public.close()
    return data


# Generate public key
def gen_public_key(private_key):
    with open('private_key.txt', 'w', encoding='utf-8') as file_object:
        file_object.write(private_key)
    try:
        with open('public_key.txt', encoding='utf-8') as file_object:
            public_key = file_object.readline().strip()
        os.remove('private_key.txt')
        os.remove('public_key.txt')
        return {"status": 'success', "msg": "", "data": public_key}
    except subprocess.CalledProcessError:
        os.remove('private_key.txt')
        return {"status": 'failed', "msg": "Key is not the correct length or format", "data": ""}


# Check if private key and public key match
def f_check_key_match(private_key, public_key, config_name):
    result = gen_public_key(private_key)
    if result['status'] == 'failed':
        return result
    else:
        sem.acquire(timeout=1)
        db = TinyDB(os.path.join(db_path, config_name + ".json"))
        peers = Query()
        match = db.search(peers.id == result['data'])
        if len(match) != 1 or result['data'] != public_key:
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return {'status': 'failed', 'msg': 'Please check your private key, it does not match with the public key.'}
        else:
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return {'status': 'success'}

# Check if there is repeated allowed IP
def check_repeat_allowed_ip(public_key, ip, config_name):
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config_name + ".json"))
    peers = Query()
    peer = db.search(peers.id == public_key)
    if len(peer) != 1:
        return {'status': 'failed', 'msg': 'Peer does not exist'}
    else:
        existed_ip = db.search((peers.id != public_key) & (peers.allowed_ip == ip))
        if len(existed_ip) != 0:
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return {'status': 'failed', 'msg': "Allowed IP already taken by another peer."}
        else:
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return {'status': 'success'}


"""
Flask Functions
"""


# Before request
@app.before_request
def auth_req():
    conf = configparser.ConfigParser(strict=False)
    conf.read(DASHBOARD_CONF)
    req = conf.get("Server", "auth_req")
    session['update'] = UPDATE
    session['dashboard_version'] = DASHBOARD_VERSION
    if req == "true":
        if '/static/' not in request.path and \
                request.endpoint != "signin" and \
                request.endpoint != "signout" and \
                request.endpoint != "auth" and \
                "username" not in session:
            print("User not loggedin - Attemped access: " + str(request.endpoint))
            if request.endpoint != "index":
                session['message'] = "You need to sign in first!"
            else:
                session['message'] = ""
            return redirect(url_for("signin"))
    else:
        if request.endpoint in ['signin', 'signout', 'auth', 'settings', 'update_acct', 'update_pwd',
                                'update_app_ip_port', 'update_wg_conf_path']:
            return redirect(url_for("index"))

    return None


"""
Sign In / Sign Out
"""


# Sign In
@app.route('/signin', methods=['GET'])
def signin():
    message = ""
    if "message" in session:
        message = session['message']
        session.pop("message")
    return render_template('signin.html', message=message)


# Sign Out
@app.route('/signout', methods=['GET'])
def signout():
    if "username" in session:
        session.pop("username")
    message = "Sign out successfully!"
    return render_template('signin.html', message=message)


# Authentication
@app.route('/auth', methods=['POST'])
def auth():
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    password = hashlib.sha256(request.form['password'].encode())
    if password.hexdigest() == config["Account"]["password"] \
            and request.form['username'] == config["Account"]["username"]:
        session['username'] = request.form['username']
        config.clear()
        return redirect(url_for("index"))

    session['message'] = "Username or Password is incorrect."
    config.clear()
    return redirect(url_for("signin"))


@app.route('/', methods=['GET'])
def index():
    """
    Index Page Related
    """

    return render_template('index.html', conf=get_conf_list())


# Setting Page
@app.route('/settings', methods=['GET'])
def settings():
    """
    Setting Page Related
    """

    message = ""
    status = ""
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    if "message" in session and "message_status" in session:
        message = session['message']
        status = session['message_status']
        session.pop("message")
        session.pop("message_status")
    required_auth = config.get("Server", "auth_req")
    return render_template('settings.html', conf=get_conf_list(), message=message, status=status,
                           app_ip=config.get("Server", "app_ip"), app_port=config.get("Server", "app_port"),
                           required_auth=required_auth, wg_conf_path=config.get("Server", "wg_conf_path"),
                           peer_global_DNS=config.get("Peers", "peer_global_DNS"),
                           peer_endpoint_allowed_ip=config.get("Peers", "peer_endpoint_allowed_ip"),
                           peer_mtu=config.get("Peers", "peer_mtu"),
                           peer_keepalive=config.get("Peers", "peer_keep_alive"),
                           peer_remote_endpoint=config.get("Peers", "remote_endpoint"))


# Update account username
@app.route('/update_acct', methods=['POST'])
def update_acct():
    if len(request.form['username']) == 0:
        session['message'] = "Username cannot be empty."
        session['message_status'] = "danger"
        return redirect(url_for("settings"))
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    config.set("Account", "username", request.form['username'])
    try:
        with open(DASHBOARD_CONF, "w", encoding='utf-8') as config_object:
            config.write(config_object)
            config.clear()
        session['message'] = "Username update successfully!"
        session['message_status'] = "success"
        session['username'] = request.form['username']
        return redirect(url_for("settings"))
    except Exception:
        session['message'] = "Username update failed."
        session['message_status'] = "danger"
        config.clear()
        return redirect(url_for("settings"))


# Update peer default settting
@app.route('/update_peer_default_config', methods=['POST'])
def update_peer_default_config():
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    if len(request.form['peer_endpoint_allowed_ip']) == 0 or \
            len(request.form['peer_global_DNS']) == 0 or \
            len(request.form['peer_remote_endpoint']) == 0:
        session['message'] = "Please fill in all required boxes."
        session['message_status'] = "danger"
        return redirect(url_for("settings"))
    # Check DNS Format
    dns_addresses = request.form['peer_global_DNS']
    if not check_DNS(dns_addresses):
        session['message'] = "Peer DNS Format Incorrect."
        session['message_status'] = "danger"
        return redirect(url_for("settings"))
    dns_addresses = dns_addresses.replace(" ", "").split(',')
    dns_addresses = ",".join(dns_addresses)

    # Check Endpoint Allowed IPs
    ip = request.form['peer_endpoint_allowed_ip']
    if not check_Allowed_IPs(ip):
        session['message'] = "Peer Endpoint Allowed IPs Format Incorrect. " \
                             "Example: 192.168.1.1/32 or 192.168.1.1/32,192.168.1.2/32"
        session['message_status'] = "danger"
        return redirect(url_for("settings"))
    # Check MTU Format
    if not len(request.form['peer_mtu']) > 0 or not request.form['peer_mtu'].isdigit():
        session['message'] = "MTU format is incorrect."
        session['message_status'] = "danger"
        return redirect(url_for("settings"))
    # Check keepalive Format
    if not len(request.form['peer_keep_alive']) > 0 or not request.form['peer_keep_alive'].isdigit():
        session['message'] = "Persistent keepalive format is incorrect."
        session['message_status'] = "danger"
        return redirect(url_for("settings"))
    # Check peer remote endpoint
    if not check_remote_endpoint(request.form['peer_remote_endpoint']):
        session['message'] = "Peer Remote Endpoint format is incorrect. It can only be a valid " \
                             "IP address or valid domain (without http:// or https://). "
        session['message_status'] = "danger"
        return redirect(url_for("settings"))

    config.set("Peers", "remote_endpoint", request.form['peer_remote_endpoint'])
    config.set("Peers", "peer_keep_alive", request.form['peer_keep_alive'])
    config.set("Peers", "peer_mtu", request.form['peer_mtu'])
    config.set("Peers", "peer_endpoint_allowed_ip", ','.join(clean_IP_with_range(ip)))
    config.set("Peers", "peer_global_DNS", dns_addresses)

    try:
        with open(DASHBOARD_CONF, "w", encoding='utf-8') as conf_object:
            config.write(conf_object)
            session['message'] = "Peer Default Settings update successfully!"
            session['message_status'] = "success"
            config.clear()
        return redirect(url_for("settings"))
    except Exception:
        session['message'] = "Peer Default Settings update failed."
        session['message_status'] = "danger"
        config.clear()
        return redirect(url_for("settings"))


# Update dashboard password
@app.route('/update_pwd', methods=['POST'])
def update_pwd():
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    if hashlib.sha256(request.form['currentpass'].encode()).hexdigest() == config.get("Account", "password"):
        if hashlib.sha256(request.form['newpass'].encode()).hexdigest() == hashlib.sha256(
                request.form['repnewpass'].encode()).hexdigest():
            config.set("Account", "password", hashlib.sha256(request.form['repnewpass'].encode()).hexdigest())
            try:
                with open(DASHBOARD_CONF, "w", encoding='utf-8') as conf_object:
                    config.write(conf_object)
                    session['message'] = "Password update successfully!"
                    session['message_status'] = "success"
                    config.clear()
                    return redirect(url_for("settings"))
            except Exception:
                session['message'] = "Password update failed"
                session['message_status'] = "danger"
                config.clear()
                return redirect(url_for("settings"))
        else:
            session['message'] = "Your New Password does not match."
            session['message_status'] = "danger"
            config.clear()
            return redirect(url_for("settings"))
    else:
        session['message'] = "Your Password does not match."
        session['message_status'] = "danger"
        config.clear()
        return redirect(url_for("settings"))


# Update dashboard IP and port
@app.route('/update_app_ip_port', methods=['POST'])
def update_app_ip_port():
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    config.set("Server", "app_ip", request.form['app_ip'])
    config.set("Server", "app_port", request.form['app_port'])
    with open(DASHBOARD_CONF, "w", encoding='utf-8') as config_object:
        config.write(config_object)
        config.clear()
    os.system('bash wgd.sh restart')


# Update WireGuard configuration file path
@app.route('/update_wg_conf_path', methods=['POST'])
def update_wg_conf_path():
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    config.set("Server", "wg_conf_path", request.form['wg_conf_path'])
    with open(DASHBOARD_CONF, "w", encoding='utf-8') as config_object:
        config.write(config_object)
        config.clear()
    session['message'] = "WireGuard Configuration Path Update Successfully!"
    session['message_status'] = "success"
    os.system('bash wgd.sh restart')


# Update configuration sorting
@app.route('/update_dashboard_sort', methods=['POST'])
def update_dashbaord_sort():
    """
    Configuration Page Related
    """

    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    data = request.get_json()
    sort_tag = ['name', 'status', 'allowed_ip']
    if data['sort'] in sort_tag:
        config.set("Server", "dashboard_sort", data['sort'])
    else:
        config.set("Server", "dashboard_sort", 'status')
    with open(DASHBOARD_CONF, "w", encoding='utf-8') as config_object:
        config.write(config_object)
        config.clear()
    return "true"


# Update configuration refresh interval
@app.route('/update_dashboard_refresh_interval', methods=['POST'])
def update_dashboard_refresh_interval():
    preset_interval = ["5000", "10000", "30000", "60000"]
    if request.form["interval"] in preset_interval:
        config = configparser.ConfigParser(strict=False)
        config.read(dashboard_conf)
        config.set("Server", "dashboard_refresh_interval", str(request.form['interval']))
        with open(DASHBOARD_CONF, "w", encoding='utf-8') as config_object:
            config.write(config_object)
            config.clear()
        return "true"
    else:
        return "false"


# Configuration Page
@app.route('/configuration/<config_name>', methods=['GET'])
def configuration(config_name):
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    conf_data = {
        "name": config_name,
        "status": get_conf_status(config_name),
        "checked": ""
    }
    if conf_data['status'] == "stopped":
        conf_data['checked'] = "nope"
    else:
        conf_data['checked'] = "checked"
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    config_list = get_conf_list()
    if config_name not in [conf['conf'] for conf in config_list]:
        return render_template('index.html', conf=get_conf_list())
    return render_template('configuration.html', conf=get_conf_list(), conf_data=conf_data,
                           dashboard_refresh_interval=int(config.get("Server", "dashboard_refresh_interval")),
                           DNS=config.get("Peers", "peer_global_DNS"),
                           endpoint_allowed_ip=config.get("Peers", "peer_endpoint_allowed_ip"),
                           title=config_name,
                           mtu=config.get("Peers", "peer_MTU"),
                           keep_alive=config.get("Peers", "peer_keep_alive"))


# Get configuration details
@app.route('/get_config/<config_name>', methods=['GET'])
def get_conf(config_name):
    config_interface = read_conf_file_interface(config_name)
    search = request.args.get('search')
    if len(search) == 0:
        search = ""
    search = urllib.parse.unquote(search)
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    sort = config.get("Server", "dashboard_sort")
    peer_display_mode = config.get("Peers", "peer_display_mode")
    if "Address" not in config_interface:
        conf_address = "N/A"
    else:
        conf_address = config_interface['Address']
    conf_data = {
        "peer_data": get_peers(config_name, search, sort),
        "name": config_name,
        "status": get_conf_status(config_name),
        "total_data_usage": get_conf_total_data(config_name),
        "public_key": get_conf_pub_key(config_name),
        "listen_port": get_conf_listen_port(config_name),
        "running_peer": get_conf_running_peer_number(config_name),
        "conf_address": conf_address,
        "wg_ip": config.get("Peers","remote_endpoint"),
        "sort_tag": sort,
        "dashboard_refresh_interval": int(config.get("Server", "dashboard_refresh_interval")),
        "peer_display_mode": peer_display_mode
    }
    if conf_data['status'] == "stopped":
        conf_data['checked'] = "nope"
    else:
        conf_data['checked'] = "checked"
    print(config.get("Peers","remote_endpoint"))
    return jsonify(conf_data)
    # return render_template('get_conf.html', conf_data=conf_data, wg_ip=config.get("Peers","remote_endpoint"), sort_tag=sort,
    #                        dashboard_refresh_interval=int(config.get("Server", "dashboard_refresh_interval")), peer_display_mode=peer_display_mode)

# Turn on / off a configuration
@app.route('/switch/<config_name>', methods=['GET'])
def switch(config_name):
    if "username" not in session:
        print("not loggedin")
        return redirect(url_for("signin"))
    status = get_conf_status(config_name)
    if status == "running":
        try:
            subprocess.run("wg-quick down " + config_name,
                           check=True, shell=True, capture_output=True).stdout
        except subprocess.CalledProcessError:
            return redirect('/')
    elif status == "stopped":
        try:
            subprocess.run("wg-quick up " + config_name,
                           check=True, shell=True, capture_output=True).stdout
        except subprocess.CalledProcessError:
            return redirect('/')

    return redirect(request.referrer)


# Add peer
@app.route('/add_peer/<config_name>', methods=['POST'])
def add_peer(config_name):
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config_name + ".json"))
    peers = Query()
    data = request.get_json()
    public_key = data['public_key']
    allowed_ips = data['allowed_ips']
    endpoint_allowed_ip = data['endpoint_allowed_ip']
    DNS = data['DNS']
    enable_preshared_key = data["enable_preshared_key"]
    keys = get_conf_peer_key(config_name)
    if len(public_key) == 0 or len(dns_addresses) == 0 or len(allowed_ips) == 0 or len(endpoint_allowed_ip) == 0:
        db.close()
        try:
            sem.release()
        except RuntimeError as e:
            print("RuntimeError: cannot release un-acquired lock")
        return "Please fill in all required box."
    if not isinstance(keys, list):
        db.close()
        try:
            sem.release()
        except RuntimeError as e:
            print("RuntimeError: cannot release un-acquired lock")
        return config_name + " is not running."
    if public_key in keys:
        db.close()
        try:
            sem.release()
        except RuntimeError as e:
            print("RuntimeError: cannot release un-acquired lock")
        return "Public key already exist."
    if len(db.search(peers.allowed_ip.matches(allowed_ips))) != 0:
        db.close()
        try:
            sem.release()
        except RuntimeError as e:
            print("RuntimeError: cannot release un-acquired lock")
        return "Allowed IP already taken by another peer."
    if not check_DNS(dns_addresses):
        db.close()
        try:
            sem.release()
        except RuntimeError as e:
            print("RuntimeError: cannot release un-acquired lock")
        return "DNS formate is incorrect. Example: 1.1.1.1"
    if not check_Allowed_IPs(endpoint_allowed_ip):
        db.close()
        try:
            sem.release()
        except RuntimeError as e:
            print("RuntimeError: cannot release un-acquired lock")
        return "Endpoint Allowed IPs format is incorrect."
    if len(data['MTU']) == 0 or not data['MTU'].isdigit():
          db.close()
          try:
              sem.release()
          except RuntimeError as e:
              print("RuntimeError: cannot release un-acquired lock")
          return "MTU format is not correct."
    if len(data['keep_alive']) == 0 or not data['keep_alive'].isdigit():
          db.close()
          try:
              sem.release()
          except RuntimeError as e:
              print("RuntimeError: cannot release un-acquired lock")
          return "Persistent Keepalive format is not correct."
    try:
        if enable_preshared_key == True:
            key = subprocess.check_output("wg genpsk > tmp_psk.txt", shell=True)
            status = subprocess.check_output(f"wg set {config_name} peer {public_key} allowed-ips {allowed_ips} preshared-key tmp_psk.txt",
                                             shell=True, stderr=subprocess.STDOUT)
            os.remove("tmp_psk.txt")
        elif enable_preshared_key == False:
            status = subprocess.check_output(f"wg set {config_name} peer {public_key} allowed-ips {allowed_ips}",
                                             shell=True, stderr=subprocess.STDOUT)
        status = subprocess.check_output("wg-quick save " + config_name, shell=True, stderr=subprocess.STDOUT)

        get_all_peers_data(config_name)
        db.update({"name": data['name'], "private_key": data['private_key'], "DNS": data['DNS'],
                   "endpoint_allowed_ip": endpoint_allowed_ip},
                  peers.id == public_key)
        db.close()
        try:
            sem.release()
        except RuntimeError as e:
            print("RuntimeError: cannot release un-acquired lock")
        return "true"
    except subprocess.CalledProcessError as exc:
        db.close()
        try:
            sem.release()
        except RuntimeError as e:
            print("RuntimeError: cannot release un-acquired lock")
        return exc.output.strip()


# Remove peer
@app.route('/remove_peer/<config_name>', methods=['POST'])
def remove_peer(config_name):
    if get_conf_status(config_name) == "stopped":
        return "Your need to turn on " + config_name + " first."
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config_name + ".json"))
    peers = Query()
    data = request.get_json()
    delete_key = data['peer_id']
    keys = get_conf_peer_key(config_name)
    if not isinstance(keys, list):
        return config_name + " is not running."
    if delete_key not in keys:
        db.close()
        return "This key does not exist"
    else:
        try:
            remove_wg = subprocess.check_output(f"wg set {config_name} peer {delete_key} remove", 
                                             shell=True, stderr=subprocess.STDOUT)
            save_wg = subprocess.check_output(f"wg-quick save {config_name}",
                                             shell=True, stderr=subprocess.STDOUT)
            db.remove(peers.id == delete_key)
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return "true"
        except subprocess.CalledProcessError as exc:
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return exc.output.strip()

# Save peer settings
@app.route('/save_peer_setting/<config_name>', methods=['POST'])
def save_peer_setting(config_name):
    data = request.get_json()
    id = data['id']
    name = data['name']
    private_key = data['private_key']
    dns_addresses = data['DNS']
    allowed_ip = data['allowed_ip']
    endpoint_allowed_ip = data['endpoint_allowed_ip']
    preshared_key = data['preshared_key']
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config_name + ".json"))
    peers = Query()
    if len(db.search(peers.id == id)) == 1:
        check_ip = check_repeat_allowed_ip(id, allowed_ip, config_name)
        if not check_IP_with_range(endpoint_allowed_ip):
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return jsonify({"status": "failed", "msg": "Endpoint Allowed IPs format is incorrect."})
        if not check_DNS(dns_addresses):
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return jsonify({"status": "failed", "msg": "DNS format is incorrect."})
        if len(data['MTU']) == 0 or not data['MTU'].isdigit():
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return jsonify({"status": "failed", "msg": "MTU format is not correct."})
        if len(data['keep_alive']) == 0 or not data['keep_alive'].isdigit():
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return jsonify({"status": "failed", "msg": "Persistent Keepalive format is not correct."})
        if private_key != "":
            check_key = f_check_key_match(private_key, id, config_name)
            if check_key['status'] == "failed":
                db.close()
                try:
                    sem.release()
                except RuntimeError as e:
                    print("RuntimeError: cannot release un-acquired lock")
                return jsonify(check_key)
        if check_ip['status'] == "failed":
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return jsonify(check_ip)
        try:
            tmp_psk = open("tmp_edit_psk.txt", "w+")
            tmp_psk.write(preshared_key)
            tmp_psk.close()
            change_psk = subprocess.check_output("wg set " + config_name + " peer " + id + " preshared-key tmp_edit_psk.txt", shell=True, stderr=subprocess.STDOUT)
            if change_psk.decode("UTF-8") != "":
                db.close()
                try:
                    sem.release()
                except RuntimeError as e:
                    print("RuntimeError: cannot release un-acquired lock")
                return jsonify({"status": "failed", "msg": change_psk.decode("UTF-8")})
            if allowed_ip == "":
                allowed_ip = '""'
            allowed_ip = allowed_ip.replace(" ", "")
            change_ip = subprocess.run('wg set ' + config_name + " peer " + id + " allowed-ips " + allowed_ip,
                                       check=True, shell=True, capture_output=True, stderr=subprocess.STDOUT).stdout
            subprocess.run('wg-quick save ' + config_name,
                           check=True, shell=True, capture_output=True, stderr=subprocess.STDOUT)
            if change_ip.decode("UTF-8") != "":
                db.close()
                try:
                    sem.release()
                except RuntimeError as e:
                    print("RuntimeError: cannot release un-acquired lock")
                return jsonify({"status": "failed", "msg": change_ip.decode("UTF-8")})
            db.update(
                {
                    "name": name, 
                     "private_key": private_key,
                     "DNS": dns_addresses, 
                     "endpoint_allowed_ip": endpoint_allowed_ip,
                     "mtu": data['MTU'],
                     "keepalive":data['keep_alive'], "preshared_key": preshared_key
                }, peers.id == id)
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return jsonify({"status": "success", "msg": ""})
        except subprocess.CalledProcessError as exc:
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            return jsonify({"status": "failed", "msg": str(exc.output.decode("UTF-8").strip())})
    else:
        db.close()
        try:
            sem.release()
        except RuntimeError as e:
            print("RuntimeError: cannot release un-acquired lock")
        return jsonify({"status": "failed", "msg": "This peer does not exist."})


# Get peer settings
@app.route('/get_peer_data/<config_name>', methods=['POST'])
def get_peer_name(config_name):
    data = request.get_json()
    id = data['id']
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config_name + ".json"))
    peers = Query()
    result = db.search(peers.id == id)
    db.close()
    data = {"name": result[0]['name'], "allowed_ip": result[0]['allowed_ip'], "DNS": result[0]['DNS'],
            "private_key": result[0]['private_key'], "endpoint_allowed_ip": result[0]['endpoint_allowed_ip'],
            "mtu": result[0]['mtu'], "keep_alive": result[0]['keepalive'], "preshared_key": result[0]["preshared_key"]}

    try:
        sem.release()
    except RuntimeError as e:
        print("RuntimeError: cannot release un-acquired lock")
    return jsonify(data)


# Generate a private key
@app.route('/generate_peer', methods=['GET'])
def generate_peer():
    return jsonify(gen_private_key())


# Generate a public key from a private key
@app.route('/generate_public_key', methods=['POST'])
def generate_public_key():
    data = request.get_json()
    private_key = data['private_key']
    return jsonify(gen_public_key(private_key))


# Check if both key match
@app.route('/check_key_match/<config_name>', methods=['POST'])
def check_key_match(config_name):
    data = request.get_json()
    private_key = data['private_key']
    public_key = data['public_key']
    return jsonify(f_check_key_match(private_key, public_key, config_name))


@app.route("/qrcode/<config_name>", methods=['GET'])
def generate_qrcode(config_name):
    id = request.args.get('id')
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config_name + ".json"))
    peers = Query()
    get_peer = db.search(peers.id == id)
    config = get_dashboard_conf()
    if len(get_peer) == 1:
        peer = get_peer[0]
        if peer['private_key'] != "":
            public_key = get_conf_pub_key(config_name)
            listen_port = get_conf_listen_port(config_name)
            endpoint = config.get("Peers", "remote_endpoint") + ":" + listen_port
            private_key = peer['private_key']
            allowed_ip = peer['allowed_ip']
            dns_addresses = peer['DNS']
            mtu_value = peer['mtu']
            endpoint_allowed_ip = peer['endpoint_allowed_ip']
            keepalive = peer['keepalive']
            preshared_key = peer["preshared_key"]
            conf = {
                "public_key": public_key,
                "listen_port": listen_port,
                "endpoint": endpoint,
                "private_key": private_key,
                "allowed_ip": allowed_ip,
                "DNS": dns_addresses,
                "mtu": mtu_value,
                "endpoint_allowed_ip": endpoint_allowed_ip,
                "keepalive": keepalive,
                "preshared_key": preshared_key
            }
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")

            result = "[Interface]\nPrivateKey = "+conf['private_key']+"\nAddress = "+conf['allowed_ip']+"\nMTU = "+conf['mtu']+"\nDNS = "+conf['DNS']\
                     +"\n\n[Peer]\nPublicKey = "+conf['public_key']+"\nAllowedIPs = "+conf['endpoint_allowed_ip']+"\nPersistentKeepalive = "+conf['keepalive']+"\nEndpoint = "+conf['endpoint']
            if preshared_key != "":
                result += "\nPresharedKey = "+preshared_key

            return render_template("qrcode.html", i=result)
    else:
        db.close()
        try:
            sem.release()
        except RuntimeError as e:
            print("RuntimeError: cannot release un-acquired lock")
        return redirect("/configuration/" + config_name)


# Download configuration file
@app.route('/download/<config_name>', methods=['GET'])
def download(config_name):
    print(request.headers.get('User-Agent'))
    id = request.args.get('id')
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config_name + ".json"))
    peers = Query()
    get_peer = db.search(peers.id == id)
    config = get_dashboard_conf()
    if len(get_peer) == 1:
        peer = get_peer[0]
        if peer['private_key'] != "":
            public_key = get_conf_pub_key(config_name)
            listen_port = get_conf_listen_port(config_name)
            endpoint = config.get("Peers", "remote_endpoint") + ":" + listen_port
            private_key = peer['private_key']
            allowed_ip = peer['allowed_ip']
            dns_addresses = peer['DNS']
            mtu_value = peer['mtu']
            endpoint_allowed_ip = peer['endpoint_allowed_ip']
            keepalive = peer['keepalive']
            filename = peer['name']
            preshared_key = peer["preshared_key"]
            if len(filename) == 0:
                filename = "Untitled_Peers"
            else:
                filename = peer['name']
                # Clean filename
                illegal_filename = [".", ",", "/", "?", "<", ">", "\\", ":", "*", '|' '\"', "com1", "com2", "com3",
                                    "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4",
                                    "lpt5", "lpt6", "lpt7", "lpt8", "lpt9", "con", "nul", "prn"]
                for i in illegal_filename:
                    filename = filename.replace(i, "")
                if len(filename) == 0:
                    filename = "Untitled_Peer"
                filename = "".join(filename.split(' '))
            filename = filename + "_" + config_name
            psk = ""
            if preshared_key != "":
                psk = "\nPresharedKey = "+preshared_key
            db.close()
            try:
                sem.release()
            except RuntimeError as e:
                print("RuntimeError: cannot release un-acquired lock")
            result = "[Interface]\nPrivateKey = " + private_key + "\nAddress = " + allowed_ip + "\nDNS = " + \
                     dns_addresses + "\nMTU = " + mtu_value + "\n\n[Peer]\nPublicKey = " + \
                     public_key + "\nAllowedIPs = " + endpoint_allowed_ip + "\nEndpoint = " + \
                     endpoint + "\nPersistentKeepalive = " + keepalive + psk
            return app.response_class((yield result), mimetype='text/conf', headers={"Content-Disposition": "attachment;filename=" + filename + ".conf"})
    db.close()
    return redirect("/configuration/" + config_name)


# Switch peer display mode
@app.route('/switch_display_mode/<mode>', methods=['GET'])
def switch_display_mode(mode):
    if mode in ['list', 'grid']:
        config = configparser.ConfigParser(strict=False)
        config.read(DASHBOARD_CONF)
        config.set("Peers", "peer_display_mode", mode)
        with open(DASHBOARD_CONF, "w", encoding='utf-8') as config_object:
            config.write(config_object)
        return "true"

    return "false"


"""
Dashboard Tools Related
"""


# Get all IP for ping
@app.route('/get_ping_ip', methods=['POST'])
def get_ping_ip():
    config_name = request.form['config']
    sem.acquire(timeout=1)
    db = TinyDB(os.path.join(db_path, config + ".json"))

    html = ""
    for i in db.all():
        html += '<optgroup label="' + i['name'] + ' - ' + i['id'] + '">'
        allowed_ip = str(i['allowed_ip']).split(",")
        for k in allowed_ip:
            k = k.split("/")
            if len(k) == 2:
                html += "<option value=" + k[0] + ">" + k[0] + "</option>"
        endpoint = str(i['endpoint']).split(":")
        if len(endpoint) == 2:
            html += "<option value=" + endpoint[0] + ">" + endpoint[0] + "</option>"
        html += "</optgroup>"
    db.close()
    try:
        sem.release()
    except RuntimeError as e:
        print("RuntimeError: cannot release un-acquired lock")
    return html


# Ping IP
@app.route('/ping_ip', methods=['POST'])
def ping_ip():
    try:
        result = ping('' + request.form['ip'] + '', count=int(request.form['count']), privileged=True, source=None)
        returnjson = {
            "address": result.address,
            "is_alive": result.is_alive,
            "min_rtt": result.min_rtt,
            "avg_rtt": result.avg_rtt,
            "max_rtt": result.max_rtt,
            "package_sent": result.packets_sent,
            "package_received": result.packets_received,
            "package_loss": result.packet_loss
        }
        if returnjson['package_loss'] == 1.0:
            returnjson['package_loss'] = returnjson['package_sent']
        return jsonify(returnjson)
    except Exception:
        return "Error"


# Traceroute IP
@app.route('/traceroute_ip', methods=['POST'])
def traceroute_ip():
    try:
        result = traceroute('' + request.form['ip'] + '', first_hop=1, max_hops=30, count=1, fast=True)
        returnjson = []
        last_distance = 0
        for hop in result:
            if last_distance + 1 != hop.distance:
                returnjson.append({"hop": "*", "ip": "*", "avg_rtt": "", "min_rtt": "", "max_rtt": ""})
            returnjson.append({"hop": hop.distance, "ip": hop.address, "avg_rtt": hop.avg_rtt, "min_rtt": hop.min_rtt,
                               "max_rtt": hop.max_rtt})
            last_distance = hop.distance
        return jsonify(returnjson)
    except Exception:
        return "Error"


"""
Dashboard Initialization
"""


def init_dashboard():
    # Set Default INI File
    if not os.path.isfile(DASHBOARD_CONF):
        conf_file = open(DASHBOARD_CONF, "w+")
    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    # Defualt dashboard account setting
    if "Account" not in config:
        config['Account'] = {}
    if "username" not in config['Account']:
        config['Account']['username'] = 'admin'
    if "password" not in config['Account']:
        config['Account']['password'] = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'
    # Defualt dashboard server setting
    if "Server" not in config:
        config['Server'] = {}
    if 'wg_conf_path' not in config['Server']:
        config['Server']['wg_conf_path'] = '/etc/wireguard'
    # TODO: IPv6 for the app IP might need to configure with Gunicorn...
    if 'app_ip' not in config['Server']:
        config['Server']['app_ip'] = '0.0.0.0'
    if 'app_port' not in config['Server']:
        config['Server']['app_port'] = '10086'
    if 'auth_req' not in config['Server']:
        config['Server']['auth_req'] = 'true'
    if 'version' not in config['Server'] or config['Server']['version'] != DASHBOARD_VERSION:
        config['Server']['version'] = DASHBOARD_VERSION
    if 'dashboard_refresh_interval' not in config['Server']:
        config['Server']['dashboard_refresh_interval'] = '60000'
    if 'dashboard_sort' not in config['Server']:
        config['Server']['dashboard_sort'] = 'status'
    # Defualt dashboard peers setting
    if "Peers" not in config:
        config['Peers'] = {}
    if 'peer_global_DNS' not in config['Peers']:
        config['Peers']['peer_global_DNS'] = '1.1.1.1'
    if 'peer_endpoint_allowed_ip' not in config['Peers']:
        config['Peers']['peer_endpoint_allowed_ip'] = '0.0.0.0/0'
    if 'peer_display_mode' not in config['Peers']:
        config['Peers']['peer_display_mode'] = 'grid'
    if 'remote_endpoint' not in config['Peers']:
        config['Peers']['remote_endpoint'] = ifcfg.default_interface()['inet']
    if 'peer_MTU' not in config['Peers']:
        config['Peers']['peer_MTU'] = "1420"
    if 'peer_keep_alive' not in config['Peers']:
        config['Peers']['peer_keep_alive'] = "21"
    with open(DASHBOARD_CONF, "w", encoding='utf-8') as config_object:
        config.write(config_object)
        config.clear()


def check_update():
    """
    Dashboard check update
    """

    config = configparser.ConfigParser(strict=False)
    config.read(DASHBOARD_CONF)
    data = urllib.request.urlopen("https://api.github.com/repos/donaldzou/WGDashboard/releases").read()
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


"""
Configure DashBoard before start web-server
"""
def run_dashboard():
    init_dashboard()
    global update
    update = check_update()
    global config
    config = configparser.ConfigParser(strict=False)
    config.read(dashboard_conf)
    global app_ip
    app_ip = config.get("Server", "app_ip")
    global app_port
    app_port = config.get("Server", "app_port")
    global wg_conf_path
    wg_conf_path = config.get("Server", "wg_conf_path")
    config.clear()
    return app


"""
Get host and port for web-server
"""
def get_host_bind():
    init_dashboard()
    config = configparser.ConfigParser(strict=False)
    config.read(dashboard_conf)
    app_ip = config.get("Server", "app_ip")
    app_port = config.get("Server", "app_port")

    return app_ip, app_port


if __name__ == "__main__":
    run_dashboard()
    app.run(host=app_ip, debug=False, port=app_port)
else:
    init_dashboard()
    UPDATE = check_update()
    configuration_settings = configparser.ConfigParser(strict=False)
    configuration_settings.read(DASHBOARD_CONF)
    app_ip = configuration_settings.get("Server", "app_ip")
    app_port = configuration_settings.get("Server", "app_port")
    wg_conf_path = configuration_settings.get("Server", "wg_conf_path")
    configuration_settings.clear()
    app.run(host=app_ip, debug=False, port=app_port)