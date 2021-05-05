dashboard_version = 'v2.0'


# Python Built-in Library
import os
from flask import Flask, request, render_template, redirect, url_for, session, abort
import subprocess
from datetime import datetime, date, time, timedelta
from operator import itemgetter
import secrets
import hashlib
import json, urllib.request
import configparser
# PIP installed library
import ifcfg
from tinydb import TinyDB, Query
dashboard_conf = 'wg-dashboard.ini'
update = ""
app = Flask("Wireguard Dashboard")
app.secret_key = secrets.token_urlsafe(16)
app.config['TEMPLATES_AUTO_RELOAD'] = True
conf_data = {}



def get_conf_peer_key(config_name):
    keys = []
    try:
        peer_key = subprocess.check_output("wg show " + config_name + " peers", shell=True)
    except Exception:
        return "stopped"
    peer_key = peer_key.decode("UTF-8").split()
    for i in peer_key: keys.append(i)
    return keys


def get_conf_running_peer_number(config_name):
    running = 0
    # Get latest handshakes
    try:
        data_usage = subprocess.check_output("wg show " + config_name + " latest-handshakes", shell=True)
    except Exception:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    now = datetime.now()
    b = timedelta(minutes=2)
    for i in range(int(len(data_usage) / 2)):
        minus = now - datetime.fromtimestamp(int(data_usage[count + 1]))
        if minus < b:
            running += 1
        count += 2
    return running

def read_conf_file(config_name):
    # Read Configuration File Start
    conf_location = wg_conf_path+"/" + config_name + ".conf"
    f = open(conf_location, 'r')
    file = f.read().split("\n")
    conf_peer_data = {
        "Interface": {},
        "Peers": []
    }
    peers_start = 0
    for i in range(len(file)):
        if file[i] == "[Peer]":
            peers_start = i
            break
        else:
            if len(file[i]) > 0:
                if file[i] != "[Interface]":
                    tmp = file[i].replace(" ", "").split("=", 1)
                    if len(tmp) == 2:
                        conf_peer_data['Interface'][tmp[0]] = tmp[1]
    conf_peers = file[peers_start:]
    peer = -1
    for i in conf_peers:
        if i == "[Peer]":
            peer += 1
            conf_peer_data["Peers"].append({})
        else:
            if len(i) > 0:
                tmp = i.replace(" ", "").split("=", 1)
                if len(tmp) == 2:
                    conf_peer_data["Peers"][peer][tmp[0]] = tmp[1]
    # Read Configuration File End
    return conf_peer_data



def get_conf_peers_data(config_name):
    db = TinyDB('db/' + config_name + '.json')
    peers = Query()
    conf_peer_data = read_conf_file(config_name)

    for i in conf_peer_data['Peers']:
        if not db.search(peers.id == i['PublicKey']):
            db.insert({
                "id": i['PublicKey'],
                "name": "",
                "total_receive": 0,
                "total_sent": 0,
                "total_data": 0,
                "endpoint": 0,
                "status": 0,
                "latest_handshake": 0,
                "allowed_ip": 0,
                "traffic": []
            })

        # Get latest handshakes
        try:
            data_usage = subprocess.check_output("wg show " + config_name + " latest-handshakes", shell=True)
        except Exception:
            return "stopped"
        data_usage = data_usage.decode("UTF-8").split()
        count = 0
        now = datetime.now()
        b = timedelta(minutes=2)
        for i in range(int(len(data_usage) / 2)):
            minus = now - datetime.fromtimestamp(int(data_usage[count + 1]))
            if minus < b:
                status = "running"
            else:
                status = "stopped"
            if int(data_usage[count + 1]) > 0:
                db.update({"latest_handshake": str(minus).split(".")[0], "status": status},
                          peers.id == data_usage[count])
            else:
                db.update({"latest_handshake": "(None)", "status": status}, peers.id == data_usage[count])
            count += 2

    # Get transfer
    try:
        data_usage = subprocess.check_output("wg show " + config_name + " transfer", shell=True)
    except Exception:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    for i in range(int(len(data_usage) / 3)):
        cur_i = db.search(peers.id == data_usage[count])
        total_sent = cur_i[0]['total_sent']
        total_receive = cur_i[0]['total_receive']
        cur_total_sent = round(int(data_usage[count + 2]) / (1024 ** 3), 4)
        cur_total_receive = round(int(data_usage[count + 1]) / (1024 ** 3), 4)
        if cur_i[0]["status"] == "running":
            if total_sent <= cur_total_sent:
                total_sent = cur_total_sent
            else: total_sent += cur_total_sent

            if total_receive <= cur_total_receive:
                total_receive = cur_total_receive
            else: total_receive += cur_total_receive
            db.update({"total_receive": round(total_receive,4),
                       "total_sent": round(total_sent,4),
                       "total_data": round(total_receive + total_sent, 4)}, peers.id == data_usage[count])

        # Will get implement in the future
        # traffic = db.search(peers.id == data_usage[count])[0]['traffic']
        # traffic.append({"time": current_time, "total_receive": round(int(data_usage[count + 1]) / (1024 ** 3), 4),
        #                 "total_sent": round(int(data_usage[count + 2]) / (1024 ** 3), 4)})
        # db.update({"traffic": traffic}, peers.id == data_usage[count])

        count += 3

    # Get endpoint
    try:
        data_usage = subprocess.check_output("wg show " + config_name + " endpoints", shell=True)
    except Exception:
        return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    for i in range(int(len(data_usage) / 2)):
        db.update({"endpoint": data_usage[count + 1]}, peers.id == data_usage[count])
        count += 2

    # Get allowed ip
    for i in conf_peer_data["Peers"]:
        db.update({"allowed_ip":i.get('AllowedIPs', '(None)')}, peers.id == i["PublicKey"])


def get_peers(config_name):
    get_conf_peers_data(config_name)
    db = TinyDB('db/' + config_name + '.json')
    result = db.all()
    result = sorted(result, key=lambda d: d['status'])
    return result


def get_conf_pub_key(config_name):
    conf = configparser.ConfigParser(strict=False)
    conf.read(wg_conf_path + "/" + config_name + ".conf")
    pri = conf.get("Interface", "PrivateKey")
    pub = subprocess.check_output("echo '" + pri + "' | wg pubkey", shell=True)
    conf.clear()
    return pub.decode().strip("\n")


def get_conf_listen_port(config_name):
    conf = configparser.ConfigParser(strict=False)
    conf.read(wg_conf_path + "/" + config_name + ".conf")
    port = conf.get("Interface", "ListenPort")
    conf.clear()
    return port


def get_conf_total_data(config_name):
    db = TinyDB('db/' + config_name + '.json')
    upload_total = 0
    download_total = 0
    for i in db.all():
        upload_total += round(i['total_sent'],4)
        download_total += round(i['total_receive'],4)
    total = round(upload_total + download_total, 4)
    return [total, upload_total, download_total]


def get_conf_status(config_name):
    ifconfig = dict(ifcfg.interfaces().items())
    if config_name in ifconfig.keys():
        return "running"
    else:
        return "stopped"


def get_conf_list():
    conf = []
    for i in os.listdir(wg_conf_path):
        if not i.startswith('.'):
            if ".conf" in i:
                i = i.replace('.conf', '')
                temp = {"conf": i, "status": get_conf_status(i), "public_key": get_conf_pub_key(i)}
                # get_conf_peers_data(i)
                if temp['status'] == "running":
                    temp['checked'] = 'checked'
                else:
                    temp['checked'] = ""
                conf.append(temp)
    conf = sorted(conf, key=itemgetter('conf'))
    return conf




@app.before_request
def auth_req():
    conf = configparser.ConfigParser(strict=False)
    conf.read(dashboard_conf)
    req = conf.get("Server", "auth_req")
    session['update'] = update
    session['dashboard_version'] = dashboard_version
    if req == "true":
        if '/static/' not in request.path and \
                request.endpoint != "signin" and \
                request.endpoint != "signout" and \
                request.endpoint != "auth" and \
                "username" not in session:
            print("not loggedin")
            session['message'] = "You need to sign in first!"
            return redirect(url_for("signin"))
    else:
        if request.endpoint in ['signin', 'signout', 'auth', 'settings', 'update_acct', 'update_pwd', 'update_app_ip_port', 'update_wg_conf_path']:
            return redirect(url_for("index"))

@app.route('/signin', methods=['GET'])
def signin():
    message = ""
    if "message" in session:
        message = session['message']
        session.pop("message")
    return render_template('signin.html', message=message)


@app.route('/signout', methods=['GET'])
def signout():
    if "username" in session:
        session.pop("username")
    message = "Sign out successfully!"
    return render_template('signin.html', message=message)



@app.route('/settings', methods=['GET'])
def settings():
    message = ""
    status = ""
    config = configparser.ConfigParser(strict=False)
    config.read(dashboard_conf)
    if "message" in session and "message_status" in session:
        message = session['message']
        status = session['message_status']
        session.pop("message")
        session.pop("message_status")
    required_auth = config.get("Server", "auth_req")
    return render_template('settings.html',conf=get_conf_list(),message=message, status=status, app_ip=config.get("Server", "app_ip"), app_port=config.get("Server", "app_port"), required_auth=required_auth, wg_conf_path=config.get("Server", "wg_conf_path"))

@app.route('/auth', methods=['POST'])
def auth():
    config = configparser.ConfigParser(strict=False)
    config.read(dashboard_conf)
    password = hashlib.sha256(request.form['password'].encode())
    if password.hexdigest() == config["Account"]["password"] and request.form['username'] == config["Account"]["username"]:
        session['username'] = request.form['username']
        config.clear()
        return redirect(url_for("index"))
    else:
        session['message'] = "Username or Password is correct."
        config.clear()
        return redirect(url_for("signin"))

@app.route('/update_acct', methods=['POST'])
def update_acct():
    config = configparser.ConfigParser(strict=False)
    config.read(dashboard_conf)
    config.set("Account", "username", request.form['username'])
    try:
        config.write(open(dashboard_conf, "w"))
        session['message'] = "Username update successfully!"
        session['message_status'] = "success"
        session['username'] = request.form['username']
        config.clear()
        return redirect(url_for("settings"))
    except Exception:
        session['message'] = "Username update failed."
        session['message_status'] = "danger"
        config.clear()
        return redirect(url_for("settings"))

@app.route('/update_pwd', methods=['POST'])
def update_pwd():
    config = configparser.ConfigParser(strict=False)
    config.read(dashboard_conf)
    if hashlib.sha256(request.form['currentpass'].encode()).hexdigest() == config.get("Account", "password"):
        if hashlib.sha256(request.form['newpass'].encode()).hexdigest() ==  hashlib.sha256(request.form['repnewpass'].encode()).hexdigest():
            config.set("Account", "password", hashlib.sha256(request.form['repnewpass'].encode()).hexdigest())
            try:
                config.write(open(dashboard_conf, "w"))
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

@app.route('/update_app_ip_port', methods=['POST'])
def update_app_ip_port():
    config = configparser.ConfigParser(strict=False)
    config.read(dashboard_conf)
    config.set("Server", "app_ip", request.form['app_ip'])
    config.set("Server", "app_port", request.form['app_port'])
    config.write(open(dashboard_conf, "w"))
    config.clear()
    os.system('bash wgd.sh restart')

@app.route('/update_wg_conf_path', methods=['POST'])
def update_wg_conf_path():
    config = configparser.ConfigParser(strict=False)
    config.read(dashboard_conf)
    config.set("Server", "wg_conf_path", request.form['wg_conf_path'])
    config.write(open(dashboard_conf, "w"))
    session['message'] = "WireGuard Configuration Path Update Successfully!"
    session['message_status'] = "success"
    config.clear()
    os.system('bash wgd.sh restart')

# @app.route('/check_update_dashboard', methods=['GET'])
# def check_update_dashboard():
#    return have_update

@app.route('/', methods=['GET'])
def index():
    print(request.referrer)
    return render_template('index.html', conf=get_conf_list())

@app.route('/configuration/<config_name>', methods=['GET'])
def conf(config_name):
    conf_data = {
        "name": config_name,
        "status": get_conf_status(config_name),
        "checked": ""
    }
    if conf_data['status'] == "stopped":
        conf_data['checked'] = "nope"
    else:
        conf_data['checked'] = "checked"
    return render_template('configuration.html', conf=get_conf_list(), conf_data=conf_data)


@app.route('/get_config/<config_name>', methods=['GET'])
def get_conf(config_name):
    db = TinyDB('db/' + config_name + '.json')
    conf_data = {
        "peer_data": get_peers(config_name),
        "name": config_name,
        "status": get_conf_status(config_name),
        "total_data_usage": get_conf_total_data(config_name),
        "public_key": get_conf_pub_key(config_name),
        "listen_port": get_conf_listen_port(config_name),
        "running_peer": get_conf_running_peer_number(config_name),
    }
    if conf_data['status'] == "stopped":
        # return redirect('/')
        conf_data['checked'] = "nope"
    else:
        conf_data['checked'] = "checked"
    return render_template('get_conf.html', conf=get_conf_list(), conf_data=conf_data)


@app.route('/switch/<config_name>', methods=['GET'])
def switch(config_name):
    if "username" not in session:
        print("not loggedin")
        return redirect(url_for("signin"))
    status = get_conf_status(config_name)
    if status == "running":
        try:
            status = subprocess.check_output("wg-quick down " + config_name, shell=True)
        except Exception:
            return redirect('/')
    elif status == "stopped":
        try:
            status = subprocess.check_output("wg-quick up " + config_name, shell=True)
        except Exception:
            return redirect('/')

    return redirect(request.referrer)


@app.route('/add_peer/<config_name>', methods=['POST'])
def add_peer(config_name):
    data = request.get_json()
    public_key = data['public_key']
    allowed_ips = data['allowed_ips']
    keys = get_conf_peer_key(config_name)
    if public_key in keys:
        return "Key already exist."
    else:
        status = ""
        try:
            status = subprocess.check_output(
                "wg set " + config_name + " peer " + public_key + " allowed-ips " + allowed_ips, shell=True,
                stderr=subprocess.STDOUT)
            status = subprocess.check_output("wg-quick save " + config_name, shell=True, stderr=subprocess.STDOUT)
            return "true"
        except subprocess.CalledProcessError as exc:
            return exc.output.strip()
            # return redirect('/configuration/'+config_name)


@app.route('/remove_peer/<config_name>', methods=['POST'])
def remove_peer(config_name):
    if get_conf_status(config_name) == "stopped":
        return "Your need to turn on "+config_name+" first."

    db = TinyDB("db/" + config_name + ".json")
    peers = Query()
    data = request.get_json()
    delete_key = data['peer_id']
    keys = get_conf_peer_key(config_name)
    if delete_key not in keys:
        return "This key does not exist"
    else:
        try:
            status = subprocess.check_output("wg set " + config_name + " peer " + delete_key + " remove", shell=True,
                                             stderr=subprocess.STDOUT)
            status = subprocess.check_output("wg-quick save " + config_name, shell=True, stderr=subprocess.STDOUT)
            db.remove(peers.id == delete_key)
            return "true"
        except subprocess.CalledProcessError as exc:
            return exc.output.strip()


@app.route('/save_peer_name/<config_name>', methods=['POST'])
def save_peer_name(config_name):
    data = request.get_json()
    id = data['id']
    name = data['name']
    db = TinyDB("db/" + config_name + ".json")
    peers = Query()

    db.update({"name": name}, peers.id == id)
    return id + " " + name


@app.route('/get_peer_name/<config_name>', methods=['POST'])
def get_peer_name(config_name):
    data = request.get_json()
    id = data['id']
    db = TinyDB("db/" + config_name + ".json")
    peers = Query()
    result = db.search(peers.id == id)
    return result[0]['name']

def init_dashboard():
    # Set Default INI File
    if not os.path.isfile("wg-dashboard.ini"):
        conf_file = open("wg-dashboard.ini", "w+")
    config = configparser.ConfigParser(strict=False)
    config.read(dashboard_conf)

    if "Account" not in config:
        config['Account'] = {}
    if "username" not in config['Account']:
        config['Account']['username'] = 'admin'
    if "password" not in config['Account']:
        config['Account']['password'] = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918'

    if "Server" not in config:
        config['Server'] = {}
    if 'wg_conf_path' not in config['Server']:
        config['Server']['wg_conf_path'] = '/etc/wireguard'
    if 'app_ip' not in config['Server']:
        config['Server']['app_ip'] = '0.0.0.0'
    if 'app_port' not in config['Server']:
        config['Server']['app_port'] = '10086'
    if 'auth_req' not in config['Server']:
        config['Server']['auth_req'] = 'true'
    if 'version' not in config['Server'] or config['Server']['version'] != dashboard_version:
        config['Server']['version'] = dashboard_version
    config.write(open(dashboard_conf, "w"))
    config.clear()

def check_update():
    conf = configparser.ConfigParser(strict=False)
    conf.read(dashboard_conf)
    data = urllib.request.urlopen("https://api.github.com/repos/donaldzou/wireguard-dashboard/releases").read()
    output = json.loads(data)
    if conf.get("Server", "version") == output[0]["tag_name"]:
        return "false"
    else:
        return "true"


if __name__ == "__main__":
    init_dashboard()
    update = check_update()
    config = configparser.ConfigParser(strict=False)
    config.read('wg-dashboard.ini')
    app_ip = config.get("Server", "app_ip")
    app_port = config.get("Server", "app_port")
    wg_conf_path = config.get("Server", "wg_conf_path")
    config.clear()
    app.run(host=app_ip, debug=False, port=app_port)

