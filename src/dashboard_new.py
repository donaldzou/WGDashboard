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
from dataclasses import dataclass
from datetime import datetime, timedelta
from json import JSONEncoder
from operator import itemgetter

import flask
# PIP installed library
import ifcfg
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, g
from flask.json.provider import JSONProvider
from flask_qrcode import QRcode
from icmplib import ping, traceroute

# Import other python files
import threading

from sqlalchemy.orm import mapped_column, declarative_base, Session
from sqlalchemy import FLOAT, INT, VARCHAR, select, MetaData, DATETIME
from sqlalchemy import create_engine, inspect

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


class CustomJsonEncoder(JSONProvider):
    def dumps(self, obj, **kwargs):
        if type(obj) == WireguardConfiguration:
            return obj.toJSON()
        return json.dumps(obj)

    def loads(self, obj, **kwargs):
        return json.loads(obj, **kwargs)


app.json = CustomJsonEncoder(app)


class WireguardConfiguration:
    __parser: configparser.ConfigParser = configparser.ConfigParser(strict=False)
    __parser.optionxform = str

    Status: bool = False
    Name: str = ""
    PrivateKey: str = ""
    PublicKey: str = ""
    ListenPort: str = ""
    Address: str = ""
    DNS: str = ""
    Table: str = ""
    MTU: str = ""
    PreUp: str = ""
    PostUp: str = ""
    PreDown: str = ""
    PostDown: str = ""
    SaveConfig: bool = False

    class InvalidConfigurationFileException(Exception):
        def __init__(self, m):
            self.message = m

        def __str__(self):
            return self.message

    def __init__(self, name):
        self.Name = name
        self.__parser.read(os.path.join(WG_CONF_PATH, f'{self.Name}.conf'))
        sections = self.__parser.sections()
        if "Interface" not in sections:
            raise self.InvalidConfigurationFileException(
                "[Interface] section not found in " + os.path.join(WG_CONF_PATH, f'{self.Name}.conf'))
        interfaceConfig = dict(self.__parser.items("Interface", True))
        for i in dir(self):
            if str(i) in interfaceConfig.keys():
                if isinstance(getattr(self, i), bool):
                    setattr(self, i, _strToBool(interfaceConfig[i]))
                else:
                    setattr(self, i, interfaceConfig[i])

        if self.PrivateKey:
            self.PublicKey = self.__getPublicKey()

        # Create tables in database
        inspector = inspect(engine)
        existingTable = inspector.get_table_names()
        if self.Name not in existingTable:
            _createPeerModel(self.Name).__table__.create(engine)
        if self.Name + "_restrict_access" not in existingTable:
            _createRestrcitedPeerModel(self.Name).__table__.create(engine)
        if self.Name + "_transfer" not in existingTable:
            _createPeerTransferModel(self.Name).__table__.create(engine)

    def __getPublicKey(self) -> str:
        return subprocess.check_output(['wg', 'pubkey'], input=self.PrivateKey.encode()).decode().strip('\n')

    def toJSON(self):
        return self.__dict__


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


def ResponseObject(status=True, message=None, data=None) -> Flask.response_class:
    response = Flask.make_response(app, {
        "status": status,
        "message": message,
        "data": data
    })
    response.content_type = "application/json"
    return response


DashboardConfig = DashboardConfig()
WireguardConfigurations: [WireguardConfiguration] = []

'''
Private Functions
'''


def _strToBool(value: str) -> bool:
    return value.lower() in ("yes", "true", "t", "1", 1)


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


def _createRestrcitedPeerModel(wgConfigName):
    class PeerRestricted(Base):
        __tablename__ = wgConfigName + "_restrict_access"
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

    return PeerRestricted


def _createPeerTransferModel(wgConfigName):
    class PeerTransfer(Base):
        __tablename__ = wgConfigName + "_transfer"
        id = mapped_column(VARCHAR, primary_key=True)
        total_receive = mapped_column(FLOAT)
        total_sent = mapped_column(FLOAT)
        total_data = mapped_column(FLOAT)
        cumu_receive = mapped_column(FLOAT)
        cumu_sent = mapped_column(FLOAT)
        cumu_data = mapped_column(FLOAT)
        time = mapped_column(DATETIME)

    return PeerTransfer


def _regexMatch(regex, text):
    pattern = re.compile(regex)
    return pattern.search(text) is not None


def _getConfigurationList() -> [WireguardConfiguration]:
    configurations = []
    for i in os.listdir(WG_CONF_PATH):
        if _regexMatch("^(.{1,}).(conf)$", i):
            i = i.replace('.conf', '')
            try:
                configurations.append(WireguardConfiguration(i))
            except WireguardConfiguration.InvalidConfigurationFileException as e:
                print(f"{i} have an invalid configuration file.")
    return configurations


'''
API Routes
'''


@app.before_request
def auth_req():
    authenticationRequired = _strToBool(DashboardConfig.GetConfig("Server", "auth_req")[1])
    if authenticationRequired:
        if ('/static/' not in request.path and "username" not in session and "/" != request.path
                and "validateAuthentication" not in request.path and "authenticate" not in request.path):
            resp = Flask.make_response(app, "Not Authorized" + request.path)
            resp.status_code = 401
            return resp


@app.route('/api/validateAuthentication', methods=["GET"])
def API_ValidateAuthentication():
    token = request.cookies.get("authToken") + ""
    if token == "" or "username" not in session or session["username"] != token:
        return ResponseObject(False, "Invalid authentication")

    return ResponseObject(True)


@app.route('/api/authenticate', methods=['POST'])
def API_AuthenticateLogin():
    data = request.get_json()
    password = hashlib.sha256(data['password'].encode())
    print()
    if password.hexdigest() == DashboardConfig.GetConfig("Account", "password")[1] \
            and data['username'] == DashboardConfig.GetConfig("Account", "username")[1]:
        authToken = hashlib.sha256(f"{data['username']}{datetime.now()}".encode()).hexdigest()
        session['username'] = authToken
        resp = ResponseObject(True, "")
        resp.set_cookie("authToken", authToken)
        session.permanent = True
        return resp
    return ResponseObject(False, "Username or password is incorrect.")


@app.route('/api/getWireguardConfigurations', methods=["GET"])
def API_getWireguardConfigurations():
    pass


@app.route('/api/getDashboardConfiguration', methods=["GET"])
def API_getDashboardConfiguration():
    pass


if __name__ == "__main__":
    engine = create_engine("sqlite:///" + os.path.join(CONFIGURATION_PATH, 'db', 'wgdashboard.db'))

    _, app_ip = DashboardConfig.GetConfig("Server", "app_ip")
    _, app_port = DashboardConfig.GetConfig("Server", "app_port")
    _, WG_CONF_PATH = DashboardConfig.GetConfig("Server", "wg_conf_path")
    WireguardConfigurations = _getConfigurationList()

    app.run(host=app_ip, debug=False, port=app_port)
