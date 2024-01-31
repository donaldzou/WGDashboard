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
from typing import Dict, Any

import bcrypt
import flask
# PIP installed library
import ifcfg
import pyotp
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

    def __init__(self, name: str = None):
        if name is not None:
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

            self.Status = self.__getStatus()

            # Create tables in database
            self.__createDatabase()

    def __createDatabase(self):
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

    def __getStatus(self) -> bool:
        return self.Name in dict(ifcfg.interfaces().items()).keys()

    def toJSON(self):
        self.Status = self.__getStatus()
        return self.__dict__

    def newConfiguration(self):
        pass


def iPv46RegexCheck(ip):
    return re.match(
        '((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9a-f]{1,4}:){7}([0-9a-f]{1,4}|:))|(([0-9a-f]{1,4}:){6}(:[0-9a-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9a-f]{1,4}:){5}(((:[0-9a-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9a-f]{1,4}:){4}(((:[0-9a-f]{1,4}){1,3})|((:[0-9a-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){3}(((:[0-9a-f]{1,4}){1,4})|((:[0-9a-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){2}(((:[0-9a-f]{1,4}){1,5})|((:[0-9a-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){1}(((:[0-9a-f]{1,4}){1,6})|((:[0-9a-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9a-f]{1,4}){1,7})|((:[0-9a-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$))',
        ip)


class DashboardConfig:

    def __init__(self):
        self.__config = configparser.ConfigParser(strict=False)
        self.__config.read(DASHBOARD_CONF)
        self.hiddenAttribute = ["totp_key"]
        self.__default = {
            "Account": {
                "username": "admin",
                "password": "admin",
                "enable_totp": "false",
                "totp_key": pyotp.random_base32()
            },
            "Server": {
                "wg_conf_path": "/etc/wireguard",
                "app_ip": "0.0.0.0",
                "app_port": "10086",
                "auth_req": "true",
                "version": DASHBOARD_VERSION,
                "dashboard_refresh_interval": "60000",
                "dashboard_sort": "status",
                "dashboard_theme": "dark"
            },
            "Peers": {
                "peer_global_DNS": "1.1.1.1",
                "peer_endpoint_allowed_ip": "0.0.0.0/0",
                "peer_display_mode": "grid",
                "remote_endpoint": ifcfg.default_interface()['inet'],
                "peer_MTU": "1420",
                "peer_keep_alive": "21"
            },
            "Other": {
                "welcome_session": "true"
            }
        }

        for section, keys in self.__default.items():
            for key, value in keys.items():
                exist, currentData = self.GetConfig(section, key)
                if not exist:
                    self.SetConfig(section, key, value, True)

    def __configValidation(self, key, value: Any) -> [bool, str]:
        if type(value) is str and len(value) == 0:
            return False, "Field cannot be empty!"
        if key == "peer_global_dns":
            value = value.split(",")
            for i in value:
                try:
                    ipaddress.ip_address(i)
                except ValueError as e:
                    return False, str(e)
        if key == "peer_endpoint_allowed_ip":
            value = value.split(",")
            for i in value:
                try:
                    ipaddress.ip_network(i, strict=False)
                except Exception as e:
                    return False, str(e)
        if key == "wg_conf_path":
            if not os.path.exists(value):
                return False, f"{value} is not a valid path"
        if key == "password":
            if self.GetConfig("Account", "password")[0]:
                if not self.__checkPassword(
                        value["currentPassword"], self.GetConfig("Account", "password")[1].encode("utf-8")):
                    return False, "Current password does not match."
                if value["newPassword"] != value["repeatNewPassword"]:
                    return False, "New passwords does not match"
        return True, ""

    def generatePassword(self, plainTextPassword: str):
        return bcrypt.hashpw(plainTextPassword.encode("utf-8"), bcrypt.gensalt(rounds=12))

    def __checkPassword(self, plainTextPassword: str, hashedPassword: bytes):
        return bcrypt.checkpw(plainTextPassword.encode("utf-8"), hashedPassword)

    def SetConfig(self, section: str, key: str, value: any, init: bool = False) -> [bool, str]:
        if key in self.hiddenAttribute and not init:
            return False, None

        if not init:
            valid, msg = self.__configValidation(key, value)
            if not valid:
                return False, msg

        if section == "Account" and key == "password":
            if not init:
                value = self.generatePassword(value["newPassword"]).decode("utf-8")
            else:
                value = self.generatePassword(value).decode("utf-8")

        if section not in self.__config:
            self.__config[section] = {}

        if key not in self.__config[section].keys() or value != self.__config[section][key]:
            if type(value) is bool:
                if value:
                    self.__config[section][key] = "true"
                else:
                    self.__config[section][key] = "false"
            else:
                self.__config[section][key] = value
            return self.SaveConfig(), ""
        return True, ""

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

        if self.__config[section][key] in ["1", "yes", "true", "on"]:
            return True, True

        if self.__config[section][key] in ["0", "no", "false", "off"]:
            return True, False

        return True, self.__config[section][key]

    def toJSON(self) -> dict[str, dict[Any, Any]]:
        the_dict = {}

        for section in self.__config.sections():
            the_dict[section] = {}
            for key, val in self.__config.items(section):
                if key not in self.hiddenAttribute:
                    if val in ["1", "yes", "true", "on"]:
                        the_dict[section][key] = True
                    elif val in ["0", "no", "false", "off"]:
                        the_dict[section][key] = False
                    else:
                        the_dict[section][key] = val
        return the_dict


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
    authenticationRequired = DashboardConfig.GetConfig("Server", "auth_req")[1]
    if authenticationRequired:

        if ('/static/' not in request.path and "username" not in session and "/" != request.path
                and "validateAuthentication" not in request.path and "authenticate" not in request.path
                and "getDashboardConfiguration" not in request.path and "getDashboardTheme" not in request.path
                and "isTotpEnabled" not in request.path
        ):
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
    valid = bcrypt.checkpw(data['password'].encode("utf-8"),
                           DashboardConfig.GetConfig("Account", "password")[1].encode("utf-8"))
    totpEnabled = DashboardConfig.GetConfig("Account", "enable_totp")[1]
    totpValid = False

    if totpEnabled:
        totpValid = pyotp.TOTP(DashboardConfig.GetConfig("Account", "totp_key")[1]).now() == data['totp']

    if (valid
            and data['username'] == DashboardConfig.GetConfig("Account", "username")[1]
            and ((totpEnabled and totpValid) or not totpEnabled)
    ):
        authToken = hashlib.sha256(f"{data['username']}{datetime.now()}".encode()).hexdigest()
        session['username'] = authToken
        resp = ResponseObject(True, DashboardConfig.GetConfig("Other", "welcome_session")[1])
        resp.set_cookie("authToken", authToken)
        session.permanent = True
        return resp

    if totpEnabled:
        return ResponseObject(False, "Sorry, your username, password or OTP is incorrect.")
    else:
        return ResponseObject(False, "Sorry, your username or password is incorrect.")


@app.route('/api/signout')
def API_SignOut():
    resp = ResponseObject(True, "")
    resp.delete_cookie("authToken")
    return resp


@app.route('/api/getWireguardConfigurations', methods=["GET"])
def API_getWireguardConfigurations():
    WireguardConfigurations = _getConfigurationList()
    return ResponseObject(data=[wc.toJSON() for wc in WireguardConfigurations])


@app.route('/api/addWireguardConfiguration', methods=["POST"])
def API_addWireguardConfiguration():
    data = request.get_json()
    keys = [
        "ConfigurationName",
        "Address",
        "ListenPort",
        "PrivateKey",
        "PublicKey",
        "PresharedKey",
        "PreUp",
        "PreDown",
        "PostUp",
        "PostDown",
        "UsePreSharedKey"
    ]
    requiredKeys = [
        "ConfigurationName", "Address", "ListenPort", "PrivateKey"
    ]
    


@app.route('/api/getDashboardConfiguration', methods=["GET"])
def API_getDashboardConfiguration():
    return ResponseObject(data=DashboardConfig.toJSON())


@app.route('/api/updateDashboardConfiguration', methods=["POST"])
def API_updateDashboardConfiguration():
    data = request.get_json()
    for section in data['DashboardConfiguration'].keys():
        for key in data['DashboardConfiguration'][section].keys():
            if not DashboardConfig.SetConfig(section, key, data['DashboardConfiguration'][section][key])[0]:
                return ResponseObject(False, "Section or value is invalid.")
    return ResponseObject()


@app.route('/api/updateDashboardConfigurationItem', methods=["POST"])
def API_updateDashboardConfigurationItem():
    data = request.get_json()
    if "section" not in data.keys() or "key" not in data.keys() or "value" not in data.keys():
        return ResponseObject(False, "Invalid request.")

    valid, msg = DashboardConfig.SetConfig(
        data["section"], data["key"], data['value'])

    if not valid:
        return ResponseObject(False, msg)

    return ResponseObject()


@app.route('/api/getDashboardTheme')
def API_getDashboardTheme():
    return ResponseObject(data=DashboardConfig.GetConfig("Server", "dashboard_theme")[1])


@app.route('/api/isTotpEnabled')
def API_isTotpEnabled():
    return ResponseObject(data=DashboardConfig.GetConfig("Account", "enable_totp")[1])


@app.route('/api/Welcome_GetTotpLink')
def API_Welcome_GetTotpLink():
    if DashboardConfig.GetConfig("Other", "welcome_session")[1]:
        return ResponseObject(
            data=pyotp.totp.TOTP(DashboardConfig.GetConfig("Account", "totp_key")[1]).provisioning_uri(
                issuer_name="WGDashboard"))
    return ResponseObject(False)


@app.route('/api/Welcome_VerifyTotpLink', methods=["POST"])
def API_Welcome_VerifyTotpLink():
    data = request.get_json()
    if DashboardConfig.GetConfig("Other", "welcome_session")[1]:
        return ResponseObject(pyotp.TOTP(DashboardConfig.GetConfig("Account", "totp_key")[1]).now() == data['totp'])
    return ResponseObject(False)


@app.route('/api/Welcome_Finish', methods=["POST"])
def API_Welcome_Finish():
    data = request.get_json()
    if DashboardConfig.GetConfig("Other", "welcome_session")[1]:
        if data["username"] == "":
            return ResponseObject(False, "Username cannot be blank.")

        if data["newPassword"] == "" or len(data["newPassword"]) < 8:
            return ResponseObject(False, "Password must be at least 8 characters")

        updateUsername, updateUsernameErr = DashboardConfig.SetConfig("Account", "username", data["username"])
        updatePassword, updatePasswordErr = DashboardConfig.SetConfig("Account", "password",
                                                                      {
                                                                          "newPassword": data["newPassword"],
                                                                          "repeatNewPassword": data[
                                                                              "repeatNewPassword"],
                                                                          "currentPassword": "admin"
                                                                      })
        updateEnableTotp, updateEnableTotpErr = DashboardConfig.SetConfig("Account", "enable_totp", data["enable_totp"])

        if not updateUsername or not updatePassword or not updateEnableTotp:
            return ResponseObject(False, f"{updateUsernameErr},{updatePasswordErr},{updateEnableTotpErr}".strip(","))

        DashboardConfig.SetConfig("Other", "welcome_session", False)

    return ResponseObject()


@app.route('/', methods=['GET'])
def index():
    """
    Index page related
    @return: Template
    """
    return render_template('index_new.html')


if __name__ == "__main__":
    engine = create_engine("sqlite:///" + os.path.join(CONFIGURATION_PATH, 'db', 'wgdashboard.db'))

    _, app_ip = DashboardConfig.GetConfig("Server", "app_ip")
    _, app_port = DashboardConfig.GetConfig("Server", "app_port")
    _, WG_CONF_PATH = DashboardConfig.GetConfig("Server", "wg_conf_path")
    WireguardConfigurations = _getConfigurationList()
    app.run(host=app_ip, debug=True, port=app_port)
