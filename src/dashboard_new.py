import itertools
import random
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
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from json import JSONEncoder
from operator import itemgetter
from typing import Dict, Any

import bcrypt
# PIP installed library
import ifcfg
import psutil
import pyotp
from flask import Flask, request, render_template, redirect, url_for, session, jsonify, g
from flask.json.provider import JSONProvider
from flask_qrcode import QRcode
from json import JSONEncoder

from icmplib import ping, traceroute

# Import other python files
import threading

from sqlalchemy.orm import mapped_column, declarative_base, Session
from sqlalchemy import FLOAT, INT, VARCHAR, select, MetaData, DATETIME
from sqlalchemy import create_engine, inspect
from flask.json.provider import DefaultJSONProvider

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


class ModelEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, 'toJson'):
            return o.toJson()
        else:
            return super(ModelEncoder, self).default(o)


'''
Classes
'''


# Base = declarative_base(class_registry=dict())


class CustomJsonEncoder(DefaultJSONProvider):
    def __init__(self, app):
        super().__init__(app)

    def default(self, o):
        if isinstance(o, WireguardConfiguration) or isinstance(o, Peer):
            return o.toJson()
        return super().default(self, o)


app.json = CustomJsonEncoder(app)


class Peer:
    def __init__(self, tableData):
        # for i in range(0, len(table)):
        #     tableData[table.description[i][0]] = table[i]

        self.id = tableData["id"]
        self.private_key = tableData["private_key"]
        self.DNS = tableData["DNS"]
        self.endpoint_allowed_ip = tableData["endpoint_allowed_ip"]
        self.name = tableData["name"]
        self.total_receive = tableData["total_receive"]
        self.total_sent = tableData["total_sent"]
        self.total_data = tableData["total_data"]
        self.endpoint = tableData["endpoint"]
        self.status = tableData["status"]
        self.latest_handshake = tableData["latest_handshake"]
        self.allowed_ip = tableData["allowed_ip"]
        self.cumu_receive = tableData["cumu_receive"]
        self.cumu_sent = tableData["cumu_sent"]
        self.cumu_data = tableData["cumu_data"]
        self.mtu = tableData["mtu"]
        self.keepalive = tableData["keepalive"]
        self.remote_endpoint = tableData["remote_endpoint"]
        self.preshared_key = tableData["preshared_key"]

    def toJson(self):
        return self.__dict__

    def __repr__(self):
        return str(self.toJson())


class WireguardConfiguration:
    class InvalidConfigurationFileException(Exception):
        def __init__(self, m):
            self.message = m

        def __str__(self):
            return self.message

    def __init__(self, name: str = None, data: dict = None):
        self.__parser: configparser.ConfigParser = configparser.ConfigParser(strict=False)
        self.__parser.optionxform = str

        self.Status: bool = False
        self.Name: str = ""
        self.PrivateKey: str = ""
        self.PublicKey: str = ""
        self.ListenPort: str = ""
        self.Address: str = ""
        self.DNS: str = ""
        self.Table: str = ""
        self.MTU: str = ""
        self.PreUp: str = ""
        self.PostUp: str = ""
        self.PreDown: str = ""
        self.PostDown: str = ""
        self.SaveConfig: bool = True

        if name is not None:
            self.Name = name
            self.__parser.read_file(open(os.path.join(WG_CONF_PATH, f'{self.Name}.conf')))
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

            self.Status = self.getStatus()


        else:
            self.Name = data["ConfigurationName"]
            for i in dir(self):
                if str(i) in data.keys():
                    if isinstance(getattr(self, i), bool):
                        setattr(self, i, _strToBool(data[i]))
                    else:
                        setattr(self, i, str(data[i]))

            # self.__createDatabase()
            self.__parser["Interface"] = {
                "PrivateKey": self.PrivateKey,
                "Address": self.Address,
                "ListenPort": self.ListenPort,
                "PreUp": self.PreUp,
                "PreDown": self.PreDown,
                "PostUp": self.PostUp,
                "PostDown": self.PostDown,
                "SaveConfig": "true"
            }

            with open(os.path.join(DashboardConfig.GetConfig("Server", "wg_conf_path")[1],
                                   f"{self.Name}.conf"), "w+") as configFile:
                # print(self.__parser.sections())
                self.__parser.write(configFile)

        self.Peers = []

        # Create tables in database
        self.__createDatabase()
        self.__getPeers()

    def __createDatabase(self):
        existingTables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        existingTables = [t['name'] for t in existingTables]
        if self.Name not in existingTables:
            cursor.execute(
                """
                CREATE TABLE %s (
                    id VARCHAR NOT NULL, private_key VARCHAR NULL, DNS VARCHAR NULL, 
                    endpoint_allowed_ip VARCHAR NULL, name VARCHAR NULL, total_receive FLOAT NULL, 
                    total_sent FLOAT NULL, total_data FLOAT NULL, endpoint VARCHAR NULL, 
                    status VARCHAR NULL, latest_handshake VARCHAR NULL, allowed_ip VARCHAR NULL, 
                    cumu_receive FLOAT NULL, cumu_sent FLOAT NULL, cumu_data FLOAT NULL, mtu INT NULL, 
                    keepalive INT NULL, remote_endpoint VARCHAR NULL, preshared_key VARCHAR NULL,
                    PRIMARY KEY (id)
                )
                """ % self.Name
            )
            sqldb.commit()

        if f'{self.Name}_restrict_access' not in existingTables:
            cursor.execute(
                """
                CREATE TABLE %s_restrict_access (
                    id VARCHAR NOT NULL, private_key VARCHAR NULL, DNS VARCHAR NULL, 
                    endpoint_allowed_ip VARCHAR NULL, name VARCHAR NULL, total_receive FLOAT NULL, 
                    total_sent FLOAT NULL, total_data FLOAT NULL, endpoint VARCHAR NULL, 
                    status VARCHAR NULL, latest_handshake VARCHAR NULL, allowed_ip VARCHAR NULL, 
                    cumu_receive FLOAT NULL, cumu_sent FLOAT NULL, cumu_data FLOAT NULL, mtu INT NULL, 
                    keepalive INT NULL, remote_endpoint VARCHAR NULL, preshared_key VARCHAR NULL,
                    PRIMARY KEY (id)
                )
                """ % self.Name
            )
            sqldb.commit()
        if f'{self.Name}_transfer' not in existingTables:
            cursor.execute(
                """
                CREATE TABLE %s_transfer (
                    id VARCHAR NOT NULL, total_receive FLOAT NULL,
                    total_sent FLOAT NULL, total_data FLOAT NULL,
                    cumu_receive FLOAT NULL, cumu_sent FLOAT NULL, cumu_data FLOAT NULL, time DATETIME
                )
                """ % self.Name
            )
            sqldb.commit()
        if f'{self.Name}_deleted' not in existingTables:
            cursor.execute(
                """
                CREATE TABLE %s_deleted (
                    id VARCHAR NOT NULL, private_key VARCHAR NULL, DNS VARCHAR NULL, 
                    endpoint_allowed_ip VARCHAR NULL, name VARCHAR NULL, total_receive FLOAT NULL, 
                    total_sent FLOAT NULL, total_data FLOAT NULL, endpoint VARCHAR NULL, 
                    status VARCHAR NULL, latest_handshake VARCHAR NULL, allowed_ip VARCHAR NULL, 
                    cumu_receive FLOAT NULL, cumu_sent FLOAT NULL, cumu_data FLOAT NULL, mtu INT NULL, 
                    keepalive INT NULL, remote_endpoint VARCHAR NULL, preshared_key VARCHAR NULL,
                    PRIMARY KEY (id)
                )
                """ % self.Name
            )
            sqldb.commit()

    def __getPublicKey(self) -> str:
        return _generatePublicKey(self.PrivateKey)[1]

    def getStatus(self) -> bool:
        self.Status = self.Name in psutil.net_if_addrs().keys()
        return self.Status

    def __getPeers(self):
        self.Peers = []
        with open(os.path.join(WG_CONF_PATH, f'{self.Name}.conf'), 'r') as configFile:
            p = []
            pCounter = -1
            content = configFile.read().split('\n')
            try:
                peerStarts = content.index("[Peer]")
                content = content[peerStarts:]
                for i in content:
                    if not regex_match("#(.*)", i) and not regex_match(";(.*)", i):
                        if i == "[Peer]":
                            pCounter += 1
                            p.append({})
                        else:
                            if len(i) > 0:
                                split = re.split(r'\s*=\s*', i, 1)
                                if len(split) == 2:
                                    p[pCounter][split[0]] = split[1]
                for i in p:
                    if "PublicKey" in i.keys():
                        checkIfExist = cursor.execute("SELECT * FROM %s WHERE id = ?" % self.Name,
                                                      ((i['PublicKey']),)).fetchone()
                        if checkIfExist is None:
                            newPeer = {
                                "id": i['PublicKey'],
                                "private_key": "",
                                "DNS": DashboardConfig.GetConfig("Peers", "peer_global_DNS")[1],
                                "endpoint_allowed_ip": DashboardConfig.GetConfig("Peers", "peer_endpoint_allowed_ip")[
                                    1],
                                "name": "",
                                "total_receive": 0,
                                "total_sent": 0,
                                "total_data": 0,
                                "endpoint": "N/A",
                                "status": "stopped",
                                "latest_handshake": "N/A",
                                "allowed_ip": i.get("AllowedIPs", "N/A"),
                                "cumu_receive": 0,
                                "cumu_sent": 0,
                                "cumu_data": 0,
                                "traffic": [],
                                "mtu": DashboardConfig.GetConfig("Peers", "peer_mtu")[1],
                                "keepalive": DashboardConfig.GetConfig("Peers", "peer_keep_alive")[1],
                                "remote_endpoint": DashboardConfig.GetConfig("Peers", "remote_endpoint")[1],
                                "preshared_key": i["PresharedKey"] if "PresharedKey" in i.keys() else ""
                            }
                            cursor.execute(
                                """
                                INSERT INTO %s
                                    VALUES (:id, :private_key, :DNS, :endpoint_allowed_ip, :name, :total_receive, :total_sent, 
                                    :total_data, :endpoint, :status, :latest_handshake, :allowed_ip, :cumu_receive, :cumu_sent, 
                                    :cumu_data, :mtu, :keepalive, :remote_endpoint, :preshared_key);
                                """ % self.Name
                                , newPeer)
                            sqldb.commit()
                            self.Peers.append(Peer(newPeer))
                        else:
                            cursor.execute("UPDATE %s SET allowed_ip = ? WHERE id = ?" % self.Name,
                                           (i.get("AllowedIPs", "N/A"), i['PublicKey'],))
                            sqldb.commit()
                            self.Peers.append(Peer(checkIfExist))
            except ValueError:
                pass

    def searchPeer(self, publicKey):
        for i in self.Peers:
            if i.id == publicKey:
                return True, i
        return False, None

    def __savePeers(self):
        for i in self.Peers:
            d = i.toJson()
            sqldb.execute(
                '''
                UPDATE %s SET private_key = :private_key, 
                    DNS = :DNS, endpoint_allowed_ip = :endpoint_allowed_ip, name = :name, 
                    total_receive = :total_receive, total_sent = :total_sent, total_data = :total_data, 
                    endpoint = :endpoint, status = :status, latest_handshake = :latest_handshake, 
                    allowed_ip = :allowed_ip, cumu_receive = :cumu_receive, cumu_sent = :cumu_sent, 
                    cumu_data = :cumu_data, mtu = :mtu, keepalive = :keepalive, 
                    remote_endpoint = :remote_endpoint, preshared_key = :preshared_key WHERE id = :id
                ''' % self.Name, d
            )
        sqldb.commit()

    def getPeersLatestHandshake(self):
        try:
            latestHandshake = subprocess.check_output(f"wg show {self.Name} latest-handshakes",
                                                      shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            return "stopped"
        latestHandshake = latestHandshake.decode("UTF-8").split()
        count = 0
        now = datetime.now()
        time_delta = timedelta(minutes=2)
        for _ in range(int(len(latestHandshake) / 2)):
            minus = now - datetime.fromtimestamp(int(latestHandshake[count + 1]))
            if minus < time_delta:
                status = "running"
            else:
                status = "stopped"
            if int(latestHandshake[count + 1]) > 0:
                sqldb.execute("UPDATE %s SET latest_handshake = ?, status = ? WHERE id= ?" % self.Name
                              , (str(minus).split(".", maxsplit=1)[0], status, latestHandshake[count],))
            else:
                sqldb.execute("UPDATE %s SET latest_handshake = 'No Handshake', status = ? WHERE id= ?" % self.Name
                              , (status, latestHandshake[count],))
            sqldb.commit()
            count += 2

    def getPeersTransfer(self):
        try:
            data_usage = subprocess.check_output(f"wg show {self.Name} transfer",
                                                 shell=True, stderr=subprocess.STDOUT)
            data_usage = data_usage.decode("UTF-8").split("\n")
            data_usage = [p.split("\t") for p in data_usage]
            for i in range(len(data_usage)):
                if len(data_usage[i]) == 3:
                    cur_i = cursor.execute(
                        "SELECT total_receive, total_sent, cumu_receive, cumu_sent, status FROM %s WHERE id= ? "
                        % self.Name, (data_usage[i][0],)).fetchone()
                    if cur_i is not None:
                        total_sent = cur_i['total_sent']
                        total_receive = cur_i['total_receive']
                        cur_total_sent = round(int(data_usage[i][2]) / (1024 ** 3), 4)
                        cur_total_receive = round(int(data_usage[i][1]) / (1024 ** 3), 4)
                        cumulative_receive = cur_i['cumu_receive'] + total_receive
                        cumulative_sent = cur_i['cumu_sent'] + total_sent
                        if total_sent <= cur_total_sent and total_receive <= cur_total_receive:
                            total_sent = cur_total_sent
                            total_receive = cur_total_receive
                        else:
                            cursor.execute(
                                "UPDATE %s SET cumu_receive = ?, cumu_sent = ?, cumu_data = ? WHERE id = ?" %
                                self.Name, (round(cumulative_receive, 4), round(cumulative_sent, 4),
                                            round(cumulative_sent + cumulative_receive, 4),
                                            data_usage[i][0],))
                            total_sent = 0
                            total_receive = 0
                        cursor.execute(
                            "UPDATE %s SET total_receive = ?, total_sent = ?, total_data = ? WHERE id = ?"
                            % self.Name, (round(total_receive, 4), round(total_sent, 4),
                                          round(total_receive + total_sent, 4), data_usage[i][0],))
                        now = datetime.now()
                        now_string = now.strftime("%d/%m/%Y %H:%M:%S")
                        cursor.execute(f'''
                                    INSERT INTO %s_transfer
                                        (id, total_receive, total_sent, total_data,
                                        cumu_receive, cumu_sent, cumu_data, time)
                                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''' % self.Name, (data_usage[i][0], round(total_receive, 4), round(total_sent, 4),
                                                  round(total_receive + total_sent, 4), round(cumulative_receive, 4),
                                                  round(cumulative_sent, 4),
                                                  round(cumulative_sent + cumulative_receive, 4), now_string,))
                        sqldb.commit()
        except Exception as e:
            print("Error" + str(e))

    def getPeersEndpoint(self):
        try:
            data_usage = subprocess.check_output(f"wg show {self.Name} endpoints",
                                                 shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            return "stopped"
        data_usage = data_usage.decode("UTF-8").split()
        count = 0
        for _ in range(int(len(data_usage) / 2)):
            sqldb.execute("UPDATE %s SET endpoint = ? WHERE id = ?" % self.Name
                          , (data_usage[count + 1], data_usage[count],))
            sqldb.commit()
            count += 2

    def toggleConfiguration(self) -> [bool, str]:
        self.getStatus()
        print("Status: ", self.getStatus())
        if self.Status:
            try:
                check = subprocess.check_output(f"wg-quick down {self.Name}",
                                                shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as exc:
                return False, str(exc.output.strip().decode("utf-8"))
        else:
            try:
                check = subprocess.check_output(f"wg-quick up {self.Name}",
                                                shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as exc:
                return False, str(exc.output.strip().decode("utf-8"))
        self.getStatus()
        return True, None

    def getPeers(self):
        self.__getPeers()
        return self.Peers

    def toJson(self):
        self.Status = self.getStatus()
        return {
            "Status": self.Status,
            "Name": self.Name,
            "PrivateKey": self.PrivateKey,
            "PublicKey": self.PublicKey,
            "Address": self.Address,
            "ListenPort": self.ListenPort,
            "PreUp": self.PreUp,
            "PreDown": self.PreDown,
            "PostUp": self.PostUp,
            "PostDown": self.PostDown,
            "SaveConfig": self.SaveConfig
        }


# Regex Match
def regex_match(regex, text):
    pattern = re.compile(regex)
    return pattern.search(text) is not None


def iPv46RegexCheck(ip):
    return re.match(
        '((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9a-f]{1,4}:){7}([0-9a-f]{1,4}|:))|(([0-9a-f]{1,4}:){6}(:[0-9a-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9a-f]{1,4}:){5}(((:[0-9a-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9a-f]{1,4}:){4}(((:[0-9a-f]{1,4}){1,3})|((:[0-9a-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){3}(((:[0-9a-f]{1,4}){1,4})|((:[0-9a-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){2}(((:[0-9a-f]{1,4}){1,5})|((:[0-9a-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){1}(((:[0-9a-f]{1,4}){1,6})|((:[0-9a-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9a-f]{1,4}){1,7})|((:[0-9a-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$))',
        ip)


class DashboardConfig:

    def __init__(self):
        self.__config = configparser.ConfigParser(strict=False)
        self.__config.read_file(open(DASHBOARD_CONF))
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

    def toJson(self) -> dict[str, dict[Any, Any]]:
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
WireguardConfigurations: {str: WireguardConfiguration} = {}

'''
Private Functions
'''


def _strToBool(value: str) -> bool:
    return value.lower() in ("yes", "true", "t", "1", 1)


def _regexMatch(regex, text):
    pattern = re.compile(regex)
    return pattern.search(text) is not None


def _getConfigurationList() -> [WireguardConfiguration]:
    configurations = {}
    for i in os.listdir(WG_CONF_PATH):
        if _regexMatch("^(.{1,}).(conf)$", i):
            i = i.replace('.conf', '')
            try:
                configurations[i] = WireguardConfiguration(i)
            except WireguardConfiguration.InvalidConfigurationFileException as e:
                print(f"{i} have an invalid configuration file.")
    return configurations


def _checkIPWithRange(ip):
    ip_patterns = (
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|\/)){4}([0-9]{1,2})(,|$)",
        r"[0-9a-fA-F]{0,4}(:([0-9a-fA-F]{0,4})){1,7}\/([0-9]{1,3})(,|$)"
    )

    for match_pattern in ip_patterns:
        match_result = regex_match(match_pattern, ip)
        if match_result:
            result = match_result
            break
    else:
        result = None

    return result


def _checkIP(ip):
    ip_patterns = (
        r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}",
        r"[0-9a-fA-F]{0,4}(:([0-9a-fA-F]{0,4})){1,7}$"
    )
    for match_pattern in ip_patterns:
        match_result = regex_match(match_pattern, ip)
        if match_result:
            result = match_result
            break
    else:
        result = None

    return result


def _checkDNS(dns):
    dns = dns.replace(' ', '').split(',')
    for i in dns:
        if not (_checkIP(i) or regex_match(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z]{0,61}[a-z]", i)):
            return False
    return True


def _generatePublicKey(privateKey) -> [bool, str]:
    try:
        publicKey = subprocess.check_output(f"wg pubkey", input=privateKey.encode(), shell=True,
                                            stderr=subprocess.STDOUT)
        return True, publicKey.decode().strip('\n')
    except subprocess.CalledProcessError:
        return False, None


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
    return ResponseObject(data=[wc for wc in WireguardConfigurations.values()])


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
    ]
    requiredKeys = [
        "ConfigurationName", "Address", "ListenPort", "PrivateKey"
    ]
    for i in keys:
        if i not in data.keys() or (i in requiredKeys and len(str(data[i])) == 0):
            return ResponseObject(False, "Please provide all required parameters.")

    # Check duplicate names, ports, address
    for i in WireguardConfigurations.values():
        if i.Name == data['ConfigurationName']:
            return ResponseObject(False,
                                  f"Already have a configuration with the name \"{data['ConfigurationName']}\"",
                                  "ConfigurationName")

        if str(i.ListenPort) == str(data["ListenPort"]):
            return ResponseObject(False,
                                  f"Already have a configuration with the port \"{data['ListenPort']}\"",
                                  "ListenPort")

        if i.Address == data["Address"]:
            return ResponseObject(False,
                                  f"Already have a configuration with the address \"{data['Address']}\"",
                                  "Address")

    WireguardConfigurations[data['ConfigurationName']] = WireguardConfiguration(data=data)
    return ResponseObject()


@app.route('/api/toggleWireguardConfiguration/')
def API_toggleWireguardConfiguration():
    configurationName = request.args.get('configurationName')

    if configurationName is None or len(
            configurationName) == 0 or configurationName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Please provide a valid configuration name")

    toggleStatus, msg = WireguardConfigurations[configurationName].toggleConfiguration()

    return ResponseObject(toggleStatus, msg, WireguardConfigurations[configurationName].Status)


@app.route('/api/getDashboardConfiguration', methods=["GET"])
def API_getDashboardConfiguration():
    return ResponseObject(data=DashboardConfig.toJson())


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


@app.route('/api/updatePeerSettings/<configName>', methods=['POST'])
def API_updatePeerSettings(configName):
    data = request.get_json()
    id = data['id']

    if len(id) > 0 and configName in WireguardConfigurations.keys():
        name = data['name']
        private_key = data['private_key']
        dns_addresses = data['DNS']
        allowed_ip = data['allowed_ip']
        endpoint_allowed_ip = data['endpoint_allowed_ip']
        preshared_key = data['preshared_key']

        wireguardConfig = WireguardConfigurations[configName]
        foundPeer, peer = wireguardConfig.searchPeer(id)
        if foundPeer:
            for p in wireguardConfig.Peers:
                if allowed_ip in p.allowed_ip and p.id != peer.id:
                    return ResponseObject(False, f"Allowed IP already taken by another peer.")
            if not _checkIPWithRange(endpoint_allowed_ip):
                return ResponseObject(False, f"Endpoint Allowed IPs format is incorrect.")
            if not _checkDNS(dns_addresses):
                return ResponseObject(False, f"DNS format is incorrect.")
            if data['mtu'] < 0 or data['mtu'] > 1460:
                return ResponseObject(False, "MTU format is not correct.")
            if data['keepalive'] < 0:
                return ResponseObject(False, "Persistent Keepalive format is not correct.")
            if len(private_key) > 0:
                pubKey = _generatePublicKey(private_key)
                if not pubKey[0] or pubKey[1] != peer.id:
                    return ResponseObject(False, "Private key does not match with the public key.")

            try:
                rd = random.Random()
                uid = uuid.UUID(int=rd.getrandbits(128), version=4)
                with open(f"{uid}", "w+") as f:
                    f.write(preshared_key)
                updatePsk = subprocess.check_output(
                    f"wg set {configName} peer {peer.id} preshared-key {uid}",
                    shell=True, stderr=subprocess.STDOUT)
                os.remove(str(uid))
                if len(updatePsk.decode().strip("\n")) != 0:
                    return ResponseObject(False,
                                          "Update peer failed when updating preshared key: " + updatePsk.decode().strip(
                                              "\n"))

                allowed_ip = allowed_ip.replace(" ", "")
                updateAllowedIp = subprocess.check_output(
                    f'wg set {configName} peer {peer.id} allowed-ips "{allowed_ip}"',
                    shell=True, stderr=subprocess.STDOUT)
                if len(updateAllowedIp.decode().strip("\n")) != 0:
                    return ResponseObject(False,
                                          "Update peer failed when updating allowed IPs: " + updateAllowedIp.decode().strip(
                                              "\n"))
                saveConfig = subprocess.check_output(f"wg-quick save {configName}",
                                                     shell=True, stderr=subprocess.STDOUT)
                if f"wg showconf {configName}" not in saveConfig.decode().strip('\n'):
                    return ResponseObject(False,
                                          "Update peer failed when saving the configuration." + saveConfig.decode().strip(
                                              '\n'))

                cursor.execute(
                    '''UPDATE %s SET name = ?, private_key = ?, DNS = ?, endpoint_allowed_ip = ?, mtu = ?, 
                    keepalive = ?, preshared_key = ? WHERE id = ?''' % configName,
                    (name, private_key, dns_addresses, endpoint_allowed_ip, data["mtu"],
                     data["keepalive"], preshared_key, id,)
                )
                return ResponseObject()

            except subprocess.CalledProcessError as exc:
                return ResponseObject(False, exc.output.decode("UTF-8").strip())

    return ResponseObject(False, "Peer does not exist")


@app.route("/api/downloadPeer/<configName>")
def API_downloadPeer(configName):
    data = request.args
    if configName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration or peer does not exist")
    configuration = WireguardConfigurations[configName]
    peerFound, peer = configuration.searchPeer(data['id'])
    if len(data['id']) == 0 or not peerFound:
        return ResponseObject(False, "Configuration or peer does not exist")

    filename = peer.name
    if len(filename) == 0:
        filename = "UntitledPeer"
    filename = "".join(filename.split(' '))
    filename = f"{filename}_{configuration.Name}"
    illegal_filename = [".", ",", "/", "?", "<", ">", "\\", ":", "*", '|' '\"', "com1", "com2", "com3",
                        "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4",
                        "lpt5", "lpt6", "lpt7", "lpt8", "lpt9", "con", "nul", "prn"]
    for i in illegal_filename:
        filename = filename.replace(i, "")

    peerConfiguration = f'''[Interface]
PrivateKey = {peer.private_key}
Address = {peer.allowed_ip}
DNS = {peer.DNS}
MTU = {str(peer.mtu)}

[Peer]
PublicKey = {configuration.PublicKey}
AllowedIPs = {peer.endpoint_allowed_ip}
Endpoint = {DashboardConfig.GetConfig("Peers", "remote_endpoint")[1]}:{configuration.ListenPort}
PersistentKeepalive = {str(peer.keepalive)}
    '''
    if len(peer.preshared_key) > 0:
        peerConfiguration += f"PresharedKey = {peer.preshared_key}"
    return ResponseObject(data={
        "fileName": filename,
        "file": peerConfiguration
    })


@app.route('/api/getWireguardConfigurationInfo', methods=["GET"])
def API_getConfigurationInfo():
    configurationName = request.args.get("configurationName")
    if not configurationName or configurationName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Please provide configuration name")
    return ResponseObject(data={
        "configurationInfo": WireguardConfigurations[configurationName],
        "configurationPeers": WireguardConfigurations[configurationName].getPeers()
    })


@app.route('/api/getDashboardTheme')
def API_getDashboardTheme():
    return ResponseObject(data=DashboardConfig.GetConfig("Server", "dashboard_theme")[1])


'''
Sign Up
'''


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


def backGroundThread():
    with app.app_context():
        print("Waiting 5 sec")
        time.sleep(5)
        while True:
            for c in WireguardConfigurations.values():
                if c.getStatus():

                    try:
                        c.getPeersTransfer()
                        c.getPeersLatestHandshake()
                        c.getPeersEndpoint()
                    except Exception as e:
                        print("Error: " + str(e))
            time.sleep(10)


if __name__ == "__main__":
    engine = create_engine("sqlite:///" + os.path.join(CONFIGURATION_PATH, 'db', 'wgdashboard.db'))
    sqldb = sqlite3.connect(os.path.join(CONFIGURATION_PATH, 'db', 'wgdashboard.db'), check_same_thread=False)
    sqldb.row_factory = sqlite3.Row
    cursor = sqldb.cursor()

    _, app_ip = DashboardConfig.GetConfig("Server", "app_ip")
    _, app_port = DashboardConfig.GetConfig("Server", "app_port")
    _, WG_CONF_PATH = DashboardConfig.GetConfig("Server", "wg_conf_path")
    WireguardConfigurations = _getConfigurationList()
    bgThread = threading.Thread(target=backGroundThread)
    bgThread.daemon = True
    bgThread.start()

    app.run(host=app_ip, debug=True, port=app_port)
