import os
from flask import Flask, request, render_template
from tinydb import TinyDB, Query
import subprocess
from datetime import datetime

conf_location = "/etc/wireguard"

app = Flask("Wireguard Dashboard")
app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.config['STATIC_AUTO_RELOAD'] = True
css = ""

def get_conf_peers_data(config_name):
    peer_data = {}
    # Get key
    try: peer_key = subprocess.check_output("wg show "+config_name+" peers", shell=True)
    except Exception: return "stopped"
    peer_key = peer_key.decode("UTF-8").split()
    for i in peer_key: peer_data[i] = {}

    #Get transfer
    try: data_usage = subprocess.check_output("wg show "+config_name+" transfer", shell=True)
    except Exception: return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    upload_total = 0
    download_total = 0
    total = 0
    for i in range(int(len(data_usage)/3)):
        peer_data[data_usage[count]]['total_recive'] = round(int(data_usage[count+1])/(1024**3), 4)
        peer_data[data_usage[count]]['total_sent'] = round(int(data_usage[count+2])/(1024**3),4)
        peer_data[data_usage[count]]['total_data'] = round((int(data_usage[count+2])+int(data_usage[count+1]))/(1024**3),4)
        count += 3

    #Get endpoint
    try: data_usage = subprocess.check_output("wg show "+config_name+" endpoints", shell=True)
    except Exception: return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    for i in range(int(len(data_usage)/2)):
        peer_data[data_usage[count]]['endpoint'] = data_usage[count+1]
        count += 2

    #Get latest handshakes
    try: data_usage = subprocess.check_output("wg show "+config_name+" latest-handshakes", shell=True)
    except Exception: return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    now = datetime.now()
    
    for i in range(int(len(data_usage)/2)):
        minus = now - datetime.fromtimestamp(int(data_usage[count+1]))
        peer_data[data_usage[count]]['latest_handshake'] = minus
        count += 2
    
    #Get allowed ip
    try: data_usage = subprocess.check_output("wg show "+config_name+" allowed-ips", shell=True)
    except Exception: return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    for i in range(int(len(data_usage)/2)):
        peer_data[data_usage[count]]['allowed_ip'] = data_usage[count+1]
        count += 2

    return peer_data




def get_conf_pub_key(config_name):
    try: pub_key = subprocess.check_output("wg show "+config_name+" public-key", shell=True)
    except Exception: return "stopped"
    return pub_key.decode("UTF-8")

def get_conf_listen_port(config_name):
    try: pub_key = subprocess.check_output("wg show "+config_name+" listen-port", shell=True)
    except Exception: return "stopped"
    return pub_key.decode("UTF-8")
    


def get_conf_total_data(config_name):
    try: data_usage = subprocess.check_output("wg show "+config_name+" transfer", shell=True)
    except Exception: return "stopped"
    data_usage = data_usage.decode("UTF-8").split()
    count = 0
    upload_total = 0
    download_total = 0
    total = 0
    for i in range(int(len(data_usage)/3)):
        upload_total += int(data_usage[count+1])
        download_total += int(data_usage[count+2])
        count += 3
    
    total = round(((((upload_total+download_total)/1024)/1024)/1024),3)
    upload_total = round(((((upload_total)/1024)/1024)/1024),3)
    download_total = round(((((download_total)/1024)/1024)/1024),3)
    
    return [total, upload_total, download_total]


def get_conf_status(config_name):
    try: status = subprocess.check_output("wg show "+config_name, shell=True)
    except Exception: return "stopped"
    else: return "running" 


def get_conf_list():
    conf = []
    for i in os.listdir(conf_location):
        if ".conf" in i:
            i = i.replace('.conf','')
            temp = {"conf":i, "status":get_conf_status(i)} 
            conf.append(temp)
    return conf

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html', conf=get_conf_list())


@app.route('/configuration/<config_name>', methods=['GET'])
def conf(config_name):
    
    conf_data = {
        "name": config_name,
        "status": get_conf_status(config_name),
        "total_data_usage": get_conf_total_data(config_name),
        "public_key": get_conf_pub_key(config_name),
        "listen_port": get_conf_listen_port(config_name),
        "peer_data":get_conf_peers_data(config_name)
    }
    return render_template('configuration.html', conf=get_conf_list(), conf_data=conf_data)


app.run(host='0.0.0.0',debug=False, port=10086)
