from crypt import methods
import sqlite3
import configparser
import hashlib
import ipaddress
import json
# Python Built-in Library
import os
import secrets
import subprocess
import time
import re
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from operator import itemgetter
# PIP installed library
import ifcfg
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, g
from flask_qrcode import QRcode
from icmplib import ping, traceroute

# Import other python files
import threading

from sqlalchemy.orm import mapped_column, declarative_base, Session
from sqlalchemy import FLOAT, INT, VARCHAR, select, MetaData
from sqlalchemy import create_engine

DASHBOARD_VERSION = 'v3.1'
CONFIGURATION_PATH = os.getenv('CONFIGURATION_PATH', '.')
DB_PATH = os.path.join(CONFIGURATION_PATH, 'db')
if not os.path.isdir(DB_PATH):
    os.mkdir(DB_PATH)
DASHBOARD_CONF = os.path.join(CONFIGURATION_PATH, 'wg-dashboard.ini')

# WireGuard's configuration path
WG_CONF_PATH = None
# Dashboard Config Name
# Upgrade Required
UPDATE = None
# Flask App Configuration
app = Flask("WGDashboard")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 5206928
app.secret_key = secrets.token_urlsafe(32)
# Enable QR Code Generator
QRcode(app)

'''
Classes
'''
Base = declarative_base()


class DashboardConfig:

    def __init__(self):
        self.__config = configparser.ConfigParser(strict=False)
        self.__config.read(DASHBOARD_CONF)
        self.__default = {
            "Account": {
                "username": "admin",
                "password": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
            },
            "Server": {
                "wg_conf_path": "/etc/wireguard",
                "app_ip": "0.0.0.0",
                "app_port": "10086",
                "auth_req": "true",
                "version": DASHBOARD_VERSION,
                "dashboard_refresh_interval": "60000",
                "dashboard_sort": "status",
                "dashboard_theme": "light"
            },
            "Peers": {
                "peer_global_DNS": "1.1.1.1",
                "peer_endpoint_allowed_ip": "0.0.0.0/0",
                "peer_display_mode": "grid",
                "remote_endpoint": ifcfg.default_interface()['inet'],
                "peer_MTU": "1420",
                "peer_keep_alive": "21"
            }
        }

        for section, keys in self.__default.items():
            for key, value in keys.items():
                exist, currentData = self.GetConfig(section, key)
                if not exist:
                    self.SetConfig(section, key, value)

    def SetConfig(self, section: str, key: str, value: any) -> bool:
        if section not in self.__config:
            self.__config[section] = {}
        self.__config[section][key] = value
        return self.SaveConfig()

    def SaveConfig(self) -> bool:
        try:
            with open(DASHBOARD_CONF, "w+", encoding='utf-8') as configFile:
                self.__config.write(configFile)
            return True
        except Exception as e:
            return False

    def GetConfig(self, section, key) -> [any, bool]:
        if section not in self.__config:
            return False, None

        if key not in self.__config[section]:
            return False, None

        return True, self.__config[section][key]


def ResponseObject(status=True, message=None, data=None) -> dict:
    return {
        "status": status,
        "message": message,
        "data": data
    }


DashboardConfig = DashboardConfig()

'''
Private Functions
'''


def _createPeerModel(wgConfigName):
    class Peer(Base):
        __tablename__ = wgConfigName
        id = mapped_column(VARCHAR, primary_key=True)
        private_key = mapped_column(VARCHAR)
        DNS = mapped_column(VARCHAR)
        endpoint_allowed_ip = mapped_column(VARCHAR)
        name = mapped_column(VARCHAR)
        total_receive = mapped_column(FLOAT)
        total_sent = mapped_column(FLOAT)
        total_data = mapped_column(FLOAT)
        endpoint = mapped_column(VARCHAR)
        status = mapped_column(VARCHAR)
        latest_handshake = mapped_column(VARCHAR)
        allowed_ip = mapped_column(VARCHAR)
        cumu_receive = mapped_column(FLOAT)
        cumu_sent = mapped_column(FLOAT)
        cumu_data = mapped_column(FLOAT)
        mtu = mapped_column(INT)
        keepalive = mapped_column(INT)
        remote_endpoint = mapped_column(VARCHAR)
        preshared_key = mapped_column(VARCHAR)

    return Peer


def _regexMatch(regex, text):
    pattern = re.compile(regex)
    return pattern.search(text) is not None


def _getConfigurationList():
    conf = []
    for i in os.listdir(WG_CONF_PATH):
        if _regexMatch("^(.{1,}).(conf)$", i):
            i = i.replace('.conf', '')
            _createPeerModel(i).__table__.create(engine)
            _createPeerModel(i + "_restrict_access").__table__.create(engine)


'''
API Routes
'''


@app.route('/api/authenticate', methods=['POST'])
def API_AuthenticateLogin():
    data = request.get_json()
    password = hashlib.sha256(data['password'].encode())
    print()
    if password.hexdigest() == DashboardConfig.GetConfig("Account", "password")[1] \
            and data['username'] == DashboardConfig.GetConfig("Account", "username")[1]:
        session['username'] = data['username']
        resp = jsonify(ResponseObject(True))
        resp.set_cookie("authToken",
                        hashlib.sha256(f"{data['username']}{datetime.now()}".encode()).hexdigest())
        session.permanent = True
        return resp
    return jsonify(ResponseObject(False, "Username or password is incorrect."))


if __name__ == "__main__":
    engine = create_engine("sqlite:///" + os.path.join(CONFIGURATION_PATH, 'db', 'wgdashboard.db'))
    _, app_ip = DashboardConfig.GetConfig("Server", "app_ip")
    _, app_port = DashboardConfig.GetConfig("Server", "app_port")
    _getConfigurationList()
    app.run(host=app_ip, debug=False, port=app_port)
