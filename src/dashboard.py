# --- Standard library imports ---
import configparser
import hashlib
import ipaddress
import json
import logging
import os
import random
import re
import secrets
import shutil
import sqlite3
import subprocess
import threading
import time
import traceback
import uuid
from datetime import datetime, timedelta
from itertools import islice
from uuid import uuid4
from zipfile import ZipFile

# --- Third-party imports ---
import bcrypt
import psutil
import pyotp
import sqlalchemy
from flask import Flask, request, render_template, session, send_file, Response
from flask_cors import CORS
from flask.json.provider import DefaultJSONProvider
from icmplib import ping, traceroute
from jinja2 import Template
from packaging import version
from sqlalchemy import RowMapping

# --- Local module imports ---
from client import createClientBlueprint
from modules.Utilities import (
    RegexMatch, StringToBoolean,
    ValidateIPAddressesWithRange, ValidateDNSAddress,
    GenerateWireguardPublicKey, GenerateWireguardPrivateKey
)
from modules.Email import EmailSender
from modules.DashboardLogger import DashboardLogger
from modules.PeerJob import PeerJob
from modules.SystemStatus import SystemStatus
from modules.PeerShareLinks import PeerShareLinks
from modules.PeerJobs import PeerJobs
from modules.DashboardConfig import DashboardConfig
from modules.WireguardConfiguration import WireguardConfiguration
from modules.AmneziaWireguardConfiguration import AmneziaWireguardConfiguration
from modules.DashboardClients import DashboardClients
from modules.DashboardPlugins import DashboardPlugins
from modules.DashboardWebHooks import DashboardWebHooks
from modules.NewConfigurationTemplates import NewConfigurationTemplates

# --- Logging configuration ---
from logging.config import dictConfig


class CustomJsonEncoder(DefaultJSONProvider):
    def __init__(self, app):
        super().__init__(app)

    def default(self, o):
        if callable(getattr(o, "toJson", None)):
            return o.toJson()
        if type(o) is RowMapping:
            return dict(o)
        if type(o) is datetime:
            return o.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(self)


'''
Response Object
'''
def ResponseObject(status=True, message=None, data=None, status_code = 200) -> Flask.response_class:
    response = Flask.make_response(app, {
        "status": status,
        "message": message,
        "data": data
    })
    response.status_code = status_code
    response.content_type = "application/json"
    return response

'''
Flask App
'''
app = Flask("WGDashboard", template_folder=os.path.abspath("./static/dist/WGDashboardAdmin"))

def peerInformationBackgroundThread():
    global WireguardConfigurations
    app.logger.info("Background Thread #1 Started")
    app.logger.info("Background Thread #1 PID:" + str(threading.get_native_id()))
    delay = 6
    time.sleep(10)
    while True:
        with app.app_context():
            try:
                curKeys = list(WireguardConfigurations.keys())
                for name in curKeys:
                    if name in WireguardConfigurations.keys() and WireguardConfigurations.get(name) is not None:
                        c = WireguardConfigurations.get(name)
                        if c.getStatus():
                            c.getPeersLatestHandshake()
                            c.getPeersTransfer()
                            c.getPeersEndpoint()
                            c.getPeers()
                            if delay == 6:
                                c.logPeersTraffic()
                                c.logPeersHistoryEndpoint()
                            c.getRestrictedPeersList()
            except Exception as e:
                app.logger.error(f"[WGDashboard] Background Thread #1 Error", e)

        if delay == 6:
            delay = 1
        else:
            delay += 1
        time.sleep(10)

def peerJobScheduleBackgroundThread():
    with app.app_context():
        app.logger.info(f"Background Thread #2 Started")
        app.logger.info(f"Background Thread #2 PID:" + str(threading.get_native_id()))
        time.sleep(10)
        while True:
            try:
                AllPeerJobs.runJob()
                time.sleep(180)
            except Exception as e:
                app.logger.error("Background Thread #2 Error", e)

def gunicornConfig():
    _, app_ip = DashboardConfig.GetConfig("Server", "app_ip")
    _, app_port = DashboardConfig.GetConfig("Server", "app_port")
    return app_ip, app_port

def ProtocolsEnabled() -> list[str]:
    from shutil import which
    protocols = []
    if which('awg') is not None and which('awg-quick') is not None:
        protocols.append("awg")
    if which('wg') is not None and which('wg-quick') is not None:
        protocols.append("wg")
    return protocols

def InitWireguardConfigurationsList(startup: bool = False):
    if os.path.exists(DashboardConfig.GetConfig("Server", "wg_conf_path")[1]):
        confs = os.listdir(DashboardConfig.GetConfig("Server", "wg_conf_path")[1])
        confs.sort()
        for i in confs:
            if RegexMatch("^(.{1,}).(conf)$", i):
                i = i.replace('.conf', '')
                try:
                    if i in WireguardConfigurations.keys():
                        if WireguardConfigurations[i].configurationFileChanged():
                            with app.app_context():
                                WireguardConfigurations[i] = WireguardConfiguration(DashboardConfig, AllPeerJobs, AllPeerShareLinks, DashboardWebHooks, i)
                    else:
                        with app.app_context():
                            WireguardConfigurations[i] = WireguardConfiguration(DashboardConfig, AllPeerJobs, AllPeerShareLinks, DashboardWebHooks, i, startup=startup)
                except WireguardConfiguration.InvalidConfigurationFileException as e:
                    app.logger.error(f"{i} have an invalid configuration file.")

    if "awg" in ProtocolsEnabled():
        confs = os.listdir(DashboardConfig.GetConfig("Server", "awg_conf_path")[1])
        confs.sort()
        for i in confs:
            if RegexMatch("^(.{1,}).(conf)$", i):
                i = i.replace('.conf', '')
                try:
                    if i in WireguardConfigurations.keys():
                        if WireguardConfigurations[i].configurationFileChanged():
                            with app.app_context():
                                WireguardConfigurations[i] = AmneziaWireguardConfiguration(DashboardConfig, AllPeerJobs, AllPeerShareLinks, DashboardWebHooks, i)
                    else:
                        with app.app_context():
                            WireguardConfigurations[i] = AmneziaWireguardConfiguration(DashboardConfig, AllPeerJobs, AllPeerShareLinks, DashboardWebHooks, i, startup=startup)
                except WireguardConfiguration.InvalidConfigurationFileException as e:
                    app.logger.error(f"{i} have an invalid configuration file.")

def startThreads():
    bgThread = threading.Thread(target=peerInformationBackgroundThread, daemon=True)
    bgThread.start()
    scheduleJobThread = threading.Thread(target=peerJobScheduleBackgroundThread, daemon=True)
    scheduleJobThread.start()

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] [%(levelname)s] in [%(module)s] %(message)s',
    }},
    'root': {
        'level': 'INFO'
    }
})


WireguardConfigurations: dict[str, WireguardConfiguration] = {}
CONFIGURATION_PATH = os.getenv('CONFIGURATION_PATH', '.')

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 5206928
app.secret_key = secrets.token_urlsafe(32)
app.json = CustomJsonEncoder(app)
with app.app_context():
    SystemStatus = SystemStatus()
    DashboardConfig = DashboardConfig()
    EmailSender = EmailSender(DashboardConfig)
    AllPeerShareLinks: PeerShareLinks = PeerShareLinks(DashboardConfig, WireguardConfigurations)
    AllPeerJobs: PeerJobs = PeerJobs(DashboardConfig, WireguardConfigurations)
    DashboardLogger = DashboardLogger()
    DashboardPlugins = DashboardPlugins(app, WireguardConfigurations)
    DashboardWebHooks = DashboardWebHooks(DashboardConfig)
    NewConfigurationTemplates = NewConfigurationTemplates()
    InitWireguardConfigurationsList(startup=True)
    DashboardClients = DashboardClients(WireguardConfigurations)
    app.register_blueprint(createClientBlueprint(WireguardConfigurations, DashboardConfig, DashboardClients))

_, APP_PREFIX = DashboardConfig.GetConfig("Server", "app_prefix")
cors = CORS(app, resources={rf"{APP_PREFIX}/api/*": {
    "origins": "*",
    "methods": "DELETE, POST, GET, OPTIONS",
    "allow_headers": ["Content-Type", "wg-dashboard-apikey"]
}})
_, app_ip = DashboardConfig.GetConfig("Server", "app_ip")
_, app_port = DashboardConfig.GetConfig("Server", "app_port")
_, WG_CONF_PATH = DashboardConfig.GetConfig("Server", "wg_conf_path")


'''
API Routes
'''

def _enforce_session_auth():
    """Enforce session authentication for non-API key access."""
    white_list = [
        '/static/',
        'validateAuthentication',
        'authenticate',
        'getDashboardConfiguration',
        'getDashboardTheme',
        'getDashboardVersion',
        'sharePeer/get',
        'isTotpEnabled',
        'locale',
        '/fileDownload',
        '/client'
    ]

    path_ok = (
        ("username" in session and session.get("role") == "admin")
        or (f"{APP_PREFIX}/" == request.path or f"{APP_PREFIX}" == request.path)
        or not all(sub not in request.path for sub in white_list)
    )

    if not path_ok:
        response = Flask.make_response(app, {
            "status": False,
            "message": "Unauthorized access.",
            "data": None
        })
        response.content_type = "application/json"
        response.status_code = 401
        return response


def _login_with_token(key):
    auth_token = hashlib.sha256(f"{key}{datetime.now()}".encode()).hexdigest()
    session.update({'role': 'admin', 'username': auth_token})
    session.permanent = True
    resp = ResponseObject(True, DashboardConfig.GetConfig("Other", "welcome_session")[1])
    resp.set_cookie("authToken", auth_token)
    return resp


def _login_with_credentials(data):
    username = data.get('username')
    password = data.get('password')
    totp_code = data.get('totp')

    valid_password = bcrypt.checkpw(password.encode("utf-8"),
                                    DashboardConfig.GetConfig("Account", "password")[1].encode("utf-8"))
    totp_enabled = DashboardConfig.GetConfig("Account", "enable_totp")[1]
    totp_valid = pyotp.TOTP(DashboardConfig.GetConfig("Account", "totp_key")[1]).now() == totp_code if totp_enabled else True

    if username == DashboardConfig.GetConfig("Account", "username")[1] and valid_password and totp_valid:
        auth_token = hashlib.sha256(f"{username}{datetime.now()}".encode()).hexdigest()
        session.update({'role': 'admin', 'username': auth_token})
        session.permanent = True
        DashboardLogger.log(str(request.url), str(request.remote_addr), Message=f"Login success: {username}")
        resp = ResponseObject(True, DashboardConfig.GetConfig("Other", "welcome_session")[1])
        resp.set_cookie("authToken", auth_token)
        return resp

    DashboardLogger.log(str(request.url), str(request.remote_addr), Message=f"Login failed: {username}")
    msg = "Sorry, your username, password or OTP is incorrect." if totp_enabled else "Sorry, your username or password is incorrect."
    return ResponseObject(False, msg)


@app.before_request
def auth_req():
    # Skip preflight requests
    if request.method.lower() == 'options':
        return ResponseObject(True)

    DashboardConfig.APIAccessed = False

    # Logging
    if "api" in request.path:
        log_message = str(request.args) if request.method.upper() == "GET" else f"Request Args: {str(request.args)} Body:{str(request.get_json())}"
        DashboardLogger.log(str(request.url), str(request.remote_addr), Message=log_message)

    authentication_required = DashboardConfig.GetConfig("Server", "auth_req")[1]
    headers = request.headers

    if authentication_required:
        api_key = headers.get('wg-dashboard-apikey')
        api_key_enabled = DashboardConfig.GetConfig("Server", "dashboard_api_key")[1]

        # API key authentication
        if api_key and api_key_enabled:
            api_key_exists = any(k.Key == api_key for k in DashboardConfig.DashboardAPIKeys)
            DashboardLogger.log(str(request.url), str(request.remote_addr), Message=f"API Key Access: {api_key_exists} - Key: {api_key}")

            if not api_key_exists:
                DashboardConfig.APIAccessed = False
                response = Flask.make_response(app, {
                    "status": False,
                    "message": "API Key does not exist",
                    "data": None
                })
                response.content_type = "application/json"
                response.status_code = 401
                return response

            DashboardConfig.APIAccessed = True
        else:
            DashboardConfig.APIAccessed = False
            _enforce_session_auth()


@app.route(f'{APP_PREFIX}/api/handshake', methods=["GET", "OPTIONS"])
def API_Handshake():
    return ResponseObject(True)


@app.get(f'{APP_PREFIX}/api/validateAuthentication')
def API_ValidateAuthentication():
    token = request.cookies.get("authToken")
    auth_required = DashboardConfig.GetConfig("Server", "auth_req")[1]
    
    if auth_required and (not token or "username" not in session or session["username"] != token):
        return ResponseObject(False, "Invalid authentication.",
                              status_code=401)
    
    return ResponseObject(True)


@app.get(f'{APP_PREFIX}/api/requireAuthentication')
def API_RequireAuthentication():
    return ResponseObject(data=DashboardConfig.GetConfig("Server", "auth_req")[1])


@app.post(f'{APP_PREFIX}/api/authenticate')
def API_AuthenticateLogin():
    data = request.get_json()
    auth_req = DashboardConfig.GetConfig("Server", "auth_req")[1]

    if not auth_req:
        return ResponseObject(True, DashboardConfig.GetConfig("Other", "welcome_session")[1])

    # API key login
    if DashboardConfig.APIAccessed:
        return _login_with_token(request.headers.get('wg-dashboard-apikey'))

    # User login
    return _login_with_credentials(data)

@app.get(f'{APP_PREFIX}/api/signout')
def API_SignOut():
    resp = ResponseObject(True, "")
    resp.delete_cookie("authToken")
    session.clear()
    return resp

@app.get(f'{APP_PREFIX}/api/getWireguardConfigurations')
def API_getWireguardConfigurations():
    InitWireguardConfigurationsList()
    return ResponseObject(data=list(WireguardConfigurations.values()))

@app.get(f'{APP_PREFIX}/api/newConfigurationTemplates')
def API_NewConfigurationTemplates():
    return ResponseObject(data=NewConfigurationTemplates.GetTemplates())

@app.get(f'{APP_PREFIX}/api/newConfigurationTemplates/createTemplate')
def API_NewConfigurationTemplates_CreateTemplate():
    return ResponseObject(data=NewConfigurationTemplates.CreateTemplate().model_dump())

@app.post(f'{APP_PREFIX}/api/newConfigurationTemplates/updateTemplate')
def API_NewConfigurationTemplates_UpdateTemplate():
    data = request.get_json()
    template = data.get('Template')

    if not template:
        return ResponseObject(False, "Please provide template",
                              status_code=400)

    status, msg = NewConfigurationTemplates.UpdateTemplate(template)

    return ResponseObject(status, msg)


@app.post(f'{APP_PREFIX}/api/newConfigurationTemplates/deleteTemplate')
def API_NewConfigurationTemplates_DeleteTemplate():
    data = request.get_json()
    template = data.get('Template')

    if not template:
        return ResponseObject(False, "Please provide template",
                              status_code=400)
    
    status, msg = NewConfigurationTemplates.DeleteTemplate(template)

    return ResponseObject(status, msg)


@app.post(f'{APP_PREFIX}/api/addWireguardConfiguration')
def API_addWireguardConfiguration():
    data = request.get_json()
    protocol = data.get("Protocol")

    required_keys = {"ConfigurationName", "Address", "ListenPort", "PrivateKey", "Protocol"}
    if not required_keys.issubset(data.keys()):
        return ResponseObject(False, "Please provide all required parameters.", status_code=400)

    if protocol not in ProtocolsEnabled():
        return ResponseObject(False, "Please provide a valid protocol: wg / awg.", status_code=400)

    for cfg in WireguardConfigurations.values():
        duplicates = {
            "ConfigurationName": cfg.Name == data['ConfigurationName'],
            "ListenPort": str(cfg.ListenPort) == str(data["ListenPort"]),
            "Address": cfg.Address == data["Address"]
        }
        for key, is_duplicate in duplicates.items():
            if is_duplicate:
                return ResponseObject(
                    False,
                    f"Already have a configuration with the {key.lower()} \"{data[key]}\"",
                    key,
                    status_code=400
                )

    paths = {
        "wg": DashboardConfig.GetConfig("Server", "wg_conf_path")[1],
        "awg": DashboardConfig.GetConfig("Server", "awg_conf_path")[1]
    }

    if "Backup" in data:
        backup_file = data["Backup"]
        protocol_detected = None
        for proto, base_path in paths.items():
            conf_path = os.path.join(base_path, 'WGDashboard_Backup', backup_file)
            sql_path = os.path.join(base_path, 'WGDashboard_Backup', backup_file.replace('.conf', '.sql'))
            if os.path.exists(conf_path) and os.path.exists(sql_path):
                protocol_detected = proto
                break

        if not protocol_detected:
            return ResponseObject(False, "Backup does not exist", status_code=400)

        shutil.copy(
            os.path.join(paths[protocol_detected], 'WGDashboard_Backup', backup_file),
            os.path.join(paths[protocol_detected], f'{data["ConfigurationName"]}.conf')
        )
        protocol = protocol_detected  # Use backup protocol
    else:
        conf_path = os.path.join(paths[protocol], f'{data["ConfigurationName"]}.conf')
        if not os.path.exists(conf_path):
            with open(conf_path, 'w') as f:
                f.write(
                    f"[Interface]\n"
                    f"Address = {data['Address']}\n"
                    f"ListenPort = {data['ListenPort']}\n"
                    f"PrivateKey = {data['PrivateKey']}\n"
                )
            os.chmod(conf_path, 0o600)  # secure file permissions

    ConfigClass = WireguardConfiguration if protocol == "wg" else AmneziaWireguardConfiguration

    WireguardConfigurations[data['ConfigurationName']] = ConfigClass(
        DashboardConfig, AllPeerJobs, AllPeerShareLinks, DashboardWebHooks,
        data=data, name=data['ConfigurationName']
    )

    return ResponseObject()


@app.get(f'{APP_PREFIX}/api/toggleWireguardConfiguration')
def API_toggleWireguardConfiguration():
    configuration_name = request.args.get('configurationName')

    if not configuration_name or configuration_name not in WireguardConfigurations:
        return ResponseObject(False, "Please provide a valid configuration name",
                              status_code=404)
    
    target_configuration = WireguardConfigurations[configuration_name]
    status, msg = target_configuration.toggleConfiguration()
    configuration_status = target_configuration.Status

    return ResponseObject(status, msg, configuration_status)


@app.post(f'{APP_PREFIX}/api/updateWireguardConfiguration')
def API_updateWireguardConfiguration():
    data = request.get_json() or {}
    name = data.get("Name")
    
    if not name:
        return ResponseObject(False, "Please provide the field: Name",
                              status_code=400)
    
    if name not in WireguardConfigurations:
        return ResponseObject(False, "Configuration does not exist",
                              status_code=404)
    
    target_configuration = WireguardConfigurations[name]
    status, msg = target_configuration.updateConfigurationSettings(data)

    return ResponseObject(status, msg, target_configuration)


@app.post(f'{APP_PREFIX}/api/updateWireguardConfigurationInfo')
def API_updateWireguardConfigurationInfo():
    data = request.get_json() or {}
    name = data.get('Name')
    key = data.get('Key')
    value = data.get('Value')

    if not all([name, key, value]): # Required values
        return ResponseObject(False, "Please provide configuration name, key, and value")

    if name not in WireguardConfigurations:
        return ResponseObject(False, "Configuration does not exist", status_code=404)
    
    target_configuration = WireguardConfigurations[name]
    status, msg, key = target_configuration.updateConfigurationInfo(key, value)

    return ResponseObject(status, msg, key)


@app.get(f'{APP_PREFIX}/api/getWireguardConfigurationRawFile')
def API_getWireguardConfigurationRawFile():
    configuration_name = request.args.get('configurationName')

    if not configuration_name or configuration_name not in WireguardConfigurations:
        return ResponseObject(False, "Please provide a valid configuration name", status_code=404)
    
    config = WireguardConfigurations[configuration_name]

    return ResponseObject(data={
        "path": config.configPath,
        "content": config.getRawConfigurationFile()
    })

@app.post(f'{APP_PREFIX}/api/updateWireguardConfigurationRawFile')
def API_UpdateWireguardConfigurationRawFile():
    data = request.get_json() or {}
    configuration_name = data.get('configurationName')
    raw_configuration = data.get('rawConfiguration')

    if not configuration_name or configuration_name not in WireguardConfigurations:
        return ResponseObject(False, "Please provide a valid configuration name")
    
    if not raw_configuration:
        return ResponseObject(False, "Please provide content")
    
    config = WireguardConfigurations[configuration_name]
    status, err = config.updateRawConfigurationFile(raw_configuration)

    return ResponseObject(status, err)

@app.post(f'{APP_PREFIX}/api/deleteWireguardConfiguration')
def API_deleteWireguardConfiguration():
    data = request.get_json() or {}
    configuration_name = data.get("ConfigurationName")

    if not configuration_name or configuration_name not in WireguardConfigurations:
        return ResponseObject(False, "Please provide the configuration name you want to delete", status_code=404)
    
    rp =  WireguardConfigurations.pop(configuration_name)
    status = rp.deleteConfiguration()

    if not status:
        WireguardConfigurations[configuration_name] = rp

    return ResponseObject(status)

@app.post(f'{APP_PREFIX}/api/renameWireguardConfiguration')
def API_renameWireguardConfiguration():
    data = request.get_json() or {}

    old_name = data.get("ConfigurationName")
    new_name = data.get("NewConfigurationName")

    if not old_name or old_name not in WireguardConfigurations:
        return ResponseObject(False, "Please provide a valid configuration name to rename", status_code=404)
    
    if not new_name:
        return ResponseObject(False, "Please provide a new configuration name", status=400)
    
    if new_name in WireguardConfigurations:
        return ResponseObject(False, "The configuration name already exists", status_code=400)
    
    rc = WireguardConfigurations.pop(old_name)
    status, message = rc.renameConfiguration(new_name)

    if status:
        if rc.Protocol == 'wg':
            ConfigClass = WireguardConfiguration
        else:
            ConfigClass = AmneziaWireguardConfiguration

        WireguardConfigurations[new_name] = ConfigClass(
            DashboardConfig, AllPeerJobs, AllPeerShareLinks, DashboardWebHooks, new_name
        )
    else:
        WireguardConfigurations[old_name] = rc

    return ResponseObject(status, message)

@app.get(f'{APP_PREFIX}/api/getWireguardConfigurationRealtimeTraffic')
def API_getWireguardConfigurationRealtimeTraffic():
    configuration_name = requests.args.get('configurationName')

    if not configuration_name or configuration_name not in WireguardConfigurations:
        return ResponseObject(False, "Configuration does not exist", status_code=404)

    rt_traffic_usage = WireguardConfigurations[configuration_name]
    return ResponseObject(data=rt_traffic_usage)

@app.get(f'{APP_PREFIX}/api/getWireguardConfigurationBackup')
def API_getWireguardConfigurationBackup():
    configuration_name = request.args.get('configurationName')

    if not configuration_name or configuration_name not in WireguardConfigurations:
        return ResponseObject(False, "Configuration does not exist",  status_code=404)

    target_configuration = WireguardConfigurations[configuration_name]
    return ResponseObject(data=target_configuration.getBackups())

@app.get(f'{APP_PREFIX}/api/getAllWireguardConfigurationBackup')
def API_getAllWireguardConfigurationBackup():
    data = {
        "ExistingConfigurations": {},
        "NonExistingConfigurations": {}
    }

    existing_configurations = WireguardConfigurations.keys()

    for single_conf in existing_configurations:
        backups = WireguardConfigurations[single_conf].getBackups(True)
        if len(backups) > 0:
            data['ExistingConfigurations'][single_conf] = WireguardConfigurations[single_conf].getBackups(True)

    for protocol in ProtocolsEnabled():
        config_path_info = DashboardConfig.GetConfig("Server", f"{protocol}_conf_path")
        configuration_path = config_path_info[1]
        backup_directory = os.path.join(configuration_path, 'WGDashboard_Backup')

        if not os.path.exists(backup_directory):
            continue

        backup_files = []
        for file_name in os.listdir(backup_directory):
            full_file_path = os.path.join(backup_directory, file_name)
            if os.path.isfile(full_file_path):
                creation_time = os.path.getctime(full_file_path)
                backup_files.append((file_name, creation_time))

        backup_files.sort(key=lambda file_info: file_info[1], reverse=True)

        for file_name, creation_time in backup_files:
            pattern = r"^(.*)_(.*)\.conf$"
            match_result = re.match(pattern, file_name)

            if not match_result:
                continue

            configuration_name = match_result.group(1)
            backup_date = match_result.group(2)

            if configuration_name in existing_configurations:
                continue

            if 'NonExistingConfigurations' not in data:
                data['NonExistingConfigurations'] = {}

            if configuration_name not in data['NonExistingConfigurations']:
                data['NonExistingConfigurations'][configuration_name] = []

            configuration_file_path = os.path.join(backup_directory, file_name)
            with open(configuration_file_path, 'r') as configuration_file:
                configuration_content = configuration_file.read()

            backup_data = {
                "protocol": protocol,
                "filename": file_name,
                "backupDate": backup_date,
                "content": configuration_content
            }

            sql_file_name = file_name.replace(".conf", ".sql")
            sql_file_path = os.path.join(backup_directory, sql_file_name)

            if os.path.isfile(sql_file_path):
                with open(sql_file_path, 'r') as sql_file:
                    sql_content = sql_file.read()

                backup_data["database"] = True
                backup_data["databaseContent"] = sql_content

            data['NonExistingConfigurations'][configuration_name].append(backup_data)

    return ResponseObject(data=data)

@app.get(f'{APP_PREFIX}/api/createWireguardConfigurationBackup')
def API_createWireguardConfigurationBackup():
    configuration_name = request.args.get('configurationName')

    if not configuration_name or configuration_name not in WireguardConfigurations:
        return ResponseObject(False, "Configuration does not exist",  status_code=404)
    
    conf_backup_file = WireguardConfigurations[configuration_name].backupConfigurationFile()[0]
    conf_backups = WireguardConfigurations[configuration_name].getBackups()

    return ResponseObject(status=conf_backup_file,data=conf_backups)

@app.post(f'{APP_PREFIX}/api/deleteWireguardConfigurationBackup')
def API_deleteWireguardConfigurationBackup():
    data = request.get_json()
    if ("ConfigurationName" not in data.keys() or 
            "BackupFileName" not in data.keys() or
            len(data['ConfigurationName']) == 0 or 
            len(data['BackupFileName']) == 0):
        return ResponseObject(False, 
        "Please provide configurationName and backupFileName in body",  status_code=400)
    configurationName = data['ConfigurationName']
    backupFileName = data['BackupFileName']
    if configurationName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration does not exist", status_code=404)
    
    status = WireguardConfigurations[configurationName].deleteBackup(backupFileName)
    return ResponseObject(status=status, message=(None if status else 'Backup file does not exist'), 
                          status_code = (200 if status else 404))

@app.get(f'{APP_PREFIX}/api/downloadWireguardConfigurationBackup')
def API_downloadWireguardConfigurationBackup():
    configurationName = request.args.get('configurationName')
    backupFileName = request.args.get('backupFileName')
    if configurationName is None or configurationName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration does not exist", status_code=404)
    status, zip = WireguardConfigurations[configurationName].downloadBackup(backupFileName)
    return ResponseObject(status, data=zip, status_code=(200 if status else 404))

@app.post(f'{APP_PREFIX}/api/restoreWireguardConfigurationBackup')
def API_restoreWireguardConfigurationBackup():
    data = request.get_json()
    configuration_name = data['ConfigurationName']
    backup_file_name = data['BackupFileName']

    if ("ConfigurationName" not in data.keys() or
            "BackupFileName" not in data.keys() or
            len(data['ConfigurationName']) == 0 or
            len(data['BackupFileName']) == 0):
        return ResponseObject(False,"Please provide ConfigurationName and BackupFileName in body", status_code=400)

    if configuration_name not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration does not exist", status_code=404)
    
    status = WireguardConfigurations[configuration_name].restoreBackup(backup_file_name)
    return ResponseObject(status=status, message=(None if status else 'Restore backup failed'))
    
@app.get(f'{APP_PREFIX}/api/getDashboardConfiguration')
def API_getDashboardConfiguration():
    return ResponseObject(data=DashboardConfig.toJson())

@app.post(f'{APP_PREFIX}/api/updateDashboardConfigurationItem')
def API_updateDashboardConfigurationItem():
    data = request.get_json()
    if "section" not in data.keys() or "key" not in data.keys() or "value" not in data.keys():
        return ResponseObject(False, "Invalid request.")
    valid, msg = DashboardConfig.SetConfig(
        data["section"], data["key"], data['value'])
    if not valid:
        return ResponseObject(False, msg)
    if data['section'] == "Server":
        if data['key'] == 'wg_conf_path':
            WireguardConfigurations.clear()
            WireguardConfigurations.clear()
            InitWireguardConfigurationsList()
    return ResponseObject(True, data=DashboardConfig.GetConfig(data["section"], data["key"])[1])

@app.get(f'{APP_PREFIX}/api/getDashboardAPIKeys')
def API_getDashboardAPIKeys():
    if DashboardConfig.GetConfig('Server', 'dashboard_api_key'):
        return ResponseObject(data=DashboardConfig.DashboardAPIKeys)
    return ResponseObject(False, "WGDashboard API Keys function is disabled")

@app.post(f'{APP_PREFIX}/api/newDashboardAPIKey')
def API_newDashboardAPIKey():
    data = request.get_json()
    if DashboardConfig.GetConfig('Server', 'dashboard_api_key'):
        try:
            if data['NeverExpire']:
                expiredAt = None
            else:
                expiredAt = datetime.strptime(data['ExpiredAt'], '%Y-%m-%d %H:%M:%S')
            DashboardConfig.createAPIKeys(expiredAt)
            return ResponseObject(True, data=DashboardConfig.DashboardAPIKeys)
        except Exception as e:
            return ResponseObject(False, str(e))
    return ResponseObject(False, "Dashboard API Keys function is disbaled")

@app.post(f'{APP_PREFIX}/api/deleteDashboardAPIKey')
def API_deleteDashboardAPIKey():
    data = request.get_json()
    if DashboardConfig.GetConfig('Server', 'dashboard_api_key'):
        if len(data['Key']) > 0 and len(list(filter(lambda x : x.Key == data['Key'], DashboardConfig.DashboardAPIKeys))) > 0:
            DashboardConfig.deleteAPIKey(data['Key'])
            return ResponseObject(True, data=DashboardConfig.DashboardAPIKeys)
        else:
            return ResponseObject(False, "API Key does not exist", status_code=404)
    return ResponseObject(False, "Dashboard API Keys function is disbaled")
    
@app.post(f'{APP_PREFIX}/api/updatePeerSettings/<configName>')
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
        mtu = data['mtu']
        keepalive = data['keepalive']
        wireguardConfig = WireguardConfigurations[configName]
        foundPeer, peer = wireguardConfig.searchPeer(id)
        if foundPeer:
            if wireguardConfig.Protocol == 'wg':
                status, msg = peer.updatePeer(name, private_key, preshared_key, dns_addresses,
                                       allowed_ip, endpoint_allowed_ip, mtu, keepalive)
            else:
                status, msg = peer.updatePeer(name, private_key, preshared_key, dns_addresses,
                    allowed_ip, endpoint_allowed_ip, mtu, keepalive, "off")
            wireguardConfig.getPeers()
            DashboardWebHooks.RunWebHook('peer_updated', {
                "configuration": wireguardConfig.Name,
                "peers": [id]
            })
            return ResponseObject(status, msg)
            
    return ResponseObject(False, "Peer does not exist")

@app.post(f'{APP_PREFIX}/api/resetPeerData/<configName>')
def API_resetPeerData(configName):
    data = request.get_json()
    id = data['id']
    type = data['type']
    if len(id) == 0 or configName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration/Peer does not exist")
    wgc = WireguardConfigurations.get(configName)
    foundPeer, peer = wgc.searchPeer(id)
    if not foundPeer:
        return ResponseObject(False, "Configuration/Peer does not exist")
    
    resetStatus = peer.resetDataUsage(type)
    if resetStatus:
        wgc.restrictPeers([id])
        wgc.allowAccessPeers([id])
    
    return ResponseObject(status=resetStatus)

@app.post(f'{APP_PREFIX}/api/deletePeers/<configName>')
def API_deletePeers(configName: str) -> ResponseObject:
    data = request.get_json()
    peers = data['peers']
    if configName in WireguardConfigurations.keys():
        if len(peers) == 0:
            return ResponseObject(False, "Please specify one or more peers", status_code=400)
        configuration = WireguardConfigurations.get(configName)
        status, msg = configuration.deletePeers(peers, AllPeerJobs, AllPeerShareLinks)
        
        # Delete Assignment
        
        for p in peers:
            assignments = DashboardClients.DashboardClientsPeerAssignment.GetAssignedClients(configName, p)
            for c in assignments:
                DashboardClients.DashboardClientsPeerAssignment.UnassignClients(c.AssignmentID)
        
        return ResponseObject(status, msg)

    return ResponseObject(False, "Configuration does not exist", status_code=404)

@app.post(f'{APP_PREFIX}/api/restrictPeers/<configName>')
def API_restrictPeers(configName: str) -> ResponseObject:
    data = request.get_json()
    peers = data['peers']
    if configName in WireguardConfigurations.keys():
        if len(peers) == 0:
            return ResponseObject(False, "Please specify one or more peers")
        configuration = WireguardConfigurations.get(configName)
        status, msg = configuration.restrictPeers(peers)
        return ResponseObject(status, msg)
    return ResponseObject(False, "Configuration does not exist", status_code=404)

@app.post(f'{APP_PREFIX}/api/sharePeer/create')
def API_sharePeer_create():
    data: dict[str, str] = request.get_json()
    Configuration = data.get('Configuration')
    Peer = data.get('Peer')
    ExpireDate = data.get('ExpireDate')
    if Configuration is None or Peer is None:
        return ResponseObject(False, "Please specify configuration and peers")
    activeLink = AllPeerShareLinks.getLink(Configuration, Peer)
    if len(activeLink) > 0:
        return ResponseObject(True, 
                              "This peer is already sharing. Please view data for shared link.",
                                data=activeLink[0]
        )
    status, message = AllPeerShareLinks.addLink(Configuration, Peer, datetime.strptime(ExpireDate, "%Y-%m-%d %H:%M:%S"))
    if not status:
        return ResponseObject(status, message)
    return ResponseObject(data=AllPeerShareLinks.getLinkByID(message))

@app.post(f'{APP_PREFIX}/api/sharePeer/update')
def API_sharePeer_update():
    data: dict[str, str] = request.get_json()
    ShareID: str = data.get("ShareID")
    ExpireDate: str = data.get("ExpireDate")
    
    if not all([ShareID, ExpireDate]):
        return ResponseObject(False, "Please specify ShareID")
    
    if len(AllPeerShareLinks.getLinkByID(ShareID)) == 0:
        return ResponseObject(False, "ShareID does not exist")
    
    status, message = AllPeerShareLinks.updateLinkExpireDate(ShareID, datetime.strptime(ExpireDate, "%Y-%m-%d %H:%M:%S"))
    if not status:
        return ResponseObject(status, message)
    return ResponseObject(data=AllPeerShareLinks.getLinkByID(ShareID))

@app.get(f'{APP_PREFIX}/api/sharePeer/get')
def API_sharePeer_get():
    data = request.args
    ShareID = data.get("ShareID")
    if ShareID is None or len(ShareID) == 0:
        return ResponseObject(False, "Please provide ShareID")
    link = AllPeerShareLinks.getLinkByID(ShareID)
    if len(link) == 0:
        return ResponseObject(False, "This link is either expired to invalid")
    l = link[0]
    if l.Configuration not in WireguardConfigurations.keys():
        return ResponseObject(False, "The peer you're looking for does not exist")
    c = WireguardConfigurations.get(l.Configuration)
    fp, p = c.searchPeer(l.Peer)
    if not fp:
        return ResponseObject(False, "The peer you're looking for does not exist")
    
    return ResponseObject(data=p.downloadPeer())
    
@app.post(f'{APP_PREFIX}/api/allowAccessPeers/<configName>')
def API_allowAccessPeers(configName: str) -> ResponseObject:
    data = request.get_json()
    peers = data['peers']
    if configName in WireguardConfigurations.keys():
        if len(peers) == 0:
            return ResponseObject(False, "Please specify one or more peers")
        configuration = WireguardConfigurations.get(configName)
        status, msg = configuration.allowAccessPeers(peers)
        return ResponseObject(status, msg)
    return ResponseObject(False, "Configuration does not exist")

@app.post(f'{APP_PREFIX}/api/addPeers/<configName>')
def API_addPeers(configName):
    if configName in WireguardConfigurations.keys():
        data: dict = request.get_json()
        try:
            

            bulkAdd: bool = data.get("bulkAdd", False)
            bulkAddAmount: int = data.get('bulkAddAmount', 0)
            preshared_key_bulkAdd: bool = data.get('preshared_key_bulkAdd', False)

            public_key: str = data.get('public_key', "")
            allowed_ips: list[str] = data.get('allowed_ips', [])
            allowed_ips_validation: bool = data.get('allowed_ips_validation', True)
            
            endpoint_allowed_ip: str = data.get('endpoint_allowed_ip', DashboardConfig.GetConfig("Peers", "peer_endpoint_allowed_ip")[1])
            dns_addresses: str = data.get('DNS', DashboardConfig.GetConfig("Peers", "peer_global_DNS")[1])
            
            
            mtu: int = data.get('mtu', None)
            keep_alive: int = data.get('keepalive', None)
            preshared_key: str = data.get('preshared_key', "")            
    
            if type(mtu) is not int or mtu < 0 or mtu > 1460:
                default: str = DashboardConfig.GetConfig("Peers", "peer_mtu")[1]
                if default.isnumeric():
                    try:
                        mtu = int(default)
                    except Exception as e:
                        mtu = 0
                else:
                    mtu = 0
            if type(keep_alive) is not int or keep_alive < 0:
                default = DashboardConfig.GetConfig("Peers", "peer_keep_alive")[1]
                if default.isnumeric():
                    try:
                        keep_alive = int(default)
                    except Exception as e:
                        keep_alive = 0
                else:
                    keep_alive = 0
            
            config = WireguardConfigurations.get(configName)
            if not config.getStatus():
                config.toggleConfiguration()
            ipStatus, availableIps = config.getAvailableIP(-1)
            ipCountStatus, numberOfAvailableIPs = config.getNumberOfAvailableIP()
            defaultIPSubnet = list(availableIps.keys())[0]
            if bulkAdd:
                if type(preshared_key_bulkAdd) is not bool:
                    preshared_key_bulkAdd = False
                if type(bulkAddAmount) is not int or bulkAddAmount < 1:
                    return ResponseObject(False, "Please specify amount of peers you want to add")
                if not ipStatus:
                    return ResponseObject(False, "No more available IP can assign")
                if len(availableIps.keys()) == 0:
                    return ResponseObject(False, "This configuration does not have any IP address available")
                if bulkAddAmount > sum(list(numberOfAvailableIPs.values())):
                    return ResponseObject(False,
                            f"The maximum number of peers can add is {sum(list(numberOfAvailableIPs.values()))}")
                keyPairs = []
                addedCount = 0
                for subnet in availableIps.keys():
                    for ip in availableIps[subnet]:
                        newPrivateKey = GenerateWireguardPrivateKey()[1]
                        addedCount += 1
                        keyPairs.append({
                            "private_key": newPrivateKey,
                            "id": GenerateWireguardPublicKey(newPrivateKey)[1],
                            "preshared_key": (GenerateWireguardPrivateKey()[1] if preshared_key_bulkAdd else ""),
                            "allowed_ip": ip,
                            "name": f"BulkPeer_{(addedCount + 1)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            "DNS": dns_addresses,
                            "endpoint_allowed_ip": endpoint_allowed_ip,
                            "mtu": mtu,
                            "keepalive": keep_alive,
                            "advanced_security": "off"
                        })
                        if addedCount == bulkAddAmount:
                            break
                    if addedCount == bulkAddAmount:
                        break
                if len(keyPairs) == 0 or (bulkAdd and len(keyPairs) != bulkAddAmount):
                    return ResponseObject(False, "Generating key pairs by bulk failed")
                status, addedPeers, message = config.addPeers(keyPairs)
                return ResponseObject(status=status, message=message, data=addedPeers)
    
            else:
                if config.searchPeer(public_key)[0] is True:
                    return ResponseObject(False, f"This peer already exist")
                name = data.get("name", "")
                private_key = data.get("private_key", "")

                if len(public_key) == 0:
                    if len(private_key) == 0:
                        private_key = GenerateWireguardPrivateKey()[1]
                        public_key = GenerateWireguardPublicKey(private_key)[1]
                    else:
                        public_key = GenerateWireguardPublicKey(private_key)[1]
                else:
                    if len(private_key) > 0:
                        genPub = GenerateWireguardPublicKey(private_key)[1]
                        # Check if provided pubkey match provided private key
                        if public_key != genPub:
                            return ResponseObject(False, "Provided Public Key does not match provided Private Key")
                if len(allowed_ips) == 0:
                    if ipStatus:
                        for subnet in availableIps.keys():
                            for ip in availableIps[subnet]:
                                allowed_ips = [ip]
                                break
                            break  
                    else:
                        return ResponseObject(False, "No more available IP can assign") 

                if allowed_ips_validation:
                    for i in allowed_ips:
                        found = False
                        for subnet in availableIps.keys():
                            network = ipaddress.ip_network(subnet, False)
                            ap = ipaddress.ip_network(i)
                            if network.version == ap.version and ap.subnet_of(network):
                                found = True
                        
                        if not found:
                            return ResponseObject(False, f"This IP is not available: {i}")

                status, addedPeers, message = config.addPeers([
                    {
                        "name": name,
                        "id": public_key,
                        "private_key": private_key,
                        "allowed_ip": ','.join(allowed_ips),
                        "preshared_key": preshared_key,
                        "endpoint_allowed_ip": endpoint_allowed_ip,
                        "DNS": dns_addresses,
                        "mtu": mtu,
                        "keepalive": keep_alive,
                        "advanced_security": "off"
                    }]
                )
                return ResponseObject(status=status, message=message, data=addedPeers)
        except Exception as e:
            app.logger.error("Add peers failed", e)
            return ResponseObject(False,
                                  f"Add peers failed. Reason: {message}")

    return ResponseObject(False, "Configuration does not exist")

@app.get(f"{APP_PREFIX}/api/downloadPeer/<configName>")
def API_downloadPeer(configName):
    data = request.args
    if configName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration does not exist")
    configuration = WireguardConfigurations[configName]
    peerFound, peer = configuration.searchPeer(data['id'])
    if len(data['id']) == 0 or not peerFound:
        return ResponseObject(False, "Peer does not exist")
    return ResponseObject(data=peer.downloadPeer())

@app.get(f"{APP_PREFIX}/api/downloadAllPeers/<configName>")
def API_downloadAllPeers(configName):
    if configName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration does not exist")
    configuration = WireguardConfigurations[configName]
    peerData = []
    untitledPeer = 0
    for i in configuration.Peers:
        file = i.downloadPeer()
        if file["fileName"] == "UntitledPeer":
            file["fileName"] = str(untitledPeer) + "_" + file["fileName"]
            untitledPeer += 1
        peerData.append(file)
    return ResponseObject(data=peerData)

@app.get(f"{APP_PREFIX}/api/getAvailableIPs/<configName>")
def API_getAvailableIPs(configName):
    if configName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration does not exist")
    status, ips = WireguardConfigurations.get(configName).getAvailableIP()
    return ResponseObject(status=status, data=ips)

@app.get(f"{APP_PREFIX}/api/getNumberOfAvailableIPs/<configName>")
def API_getNumberOfAvailableIPs(configName):
    if configName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration does not exist")
    status, ips = WireguardConfigurations.get(configName).getNumberOfAvailableIP()
    return ResponseObject(status=status, data=ips)

@app.get(f'{APP_PREFIX}/api/getWireguardConfigurationInfo')
def API_getConfigurationInfo():
    configurationName = request.args.get("configurationName")
    if not configurationName or configurationName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Please provide configuration name")
    return ResponseObject(data={
        "configurationInfo": WireguardConfigurations[configurationName],
        "configurationPeers": WireguardConfigurations[configurationName].getPeersList(),
        "configurationRestrictedPeers": WireguardConfigurations[configurationName].getRestrictedPeersList()
    })

@app.get(f'{APP_PREFIX}/api/getPeerHistoricalEndpoints')
def API_GetPeerHistoricalEndpoints():
    configurationName = request.args.get("configurationName")
    id = request.args.get('id')
    if not configurationName or not id:
        return ResponseObject(False, "Please provide configurationName and id")
    fp, p = WireguardConfigurations.get(configurationName).searchPeer(id)
    if fp:
        result = p.getEndpoints()
        geo = {}
        try:
            r = requests.post(f"http://ip-api.com/batch?fields=city,country,lat,lon,query",
                              data=json.dumps([x['endpoint'] for x in result]))
            d = r.json()
            
                
        except Exception as e:
            return ResponseObject(data=result, message="Failed to request IP address geolocation. " + str(e))
        
        return ResponseObject(data={
            "endpoints": p.getEndpoints(),
            "geolocation": d
        })
    return ResponseObject(False, "Peer does not exist")

@app.get(f'{APP_PREFIX}/api/getPeerSessions')
def API_GetPeerSessions():
    configurationName = request.args.get("configurationName")
    id = request.args.get('id')
    try:
        startDate = request.args.get('startDate', None)
        endDate = request.args.get('endDate', None)
        
        if startDate is None:
            endDate = None
        else:
            startDate = datetime.strptime(startDate, "%Y-%m-%d")
            if endDate:
                endDate = datetime.strptime(endDate, "%Y-%m-%d")
                if startDate > endDate:
                    return ResponseObject(False, "startDate must be smaller than endDate")
    except Exception as e:
        return ResponseObject(False, "Dates are invalid")
    if not configurationName or not id:
        return ResponseObject(False, "Please provide configurationName and id")
    fp, p = WireguardConfigurations.get(configurationName).searchPeer(id)
    if fp:
        return ResponseObject(data=p.getSessions(startDate, endDate))
    return ResponseObject(False, "Peer does not exist")

@app.get(f'{APP_PREFIX}/api/getPeerTraffics')
def API_GetPeerTraffics():
    configurationName = request.args.get("configurationName")
    id = request.args.get('id')
    try:
        interval = request.args.get('interval', 30)
        startDate = request.args.get('startDate', None)
        endDate = request.args.get('endDate', None)
        
        if type(interval) is str:
            if not interval.isdigit():
                return ResponseObject(False, "Interval must be integers in minutes")
            interval = int(interval)
        
        if startDate is None:
            endDate = None
        else:
            startDate = datetime.strptime(startDate, "%Y-%m-%d")
            if endDate:
                endDate = datetime.strptime(endDate, "%Y-%m-%d")
                if startDate > endDate:
                    return ResponseObject(False, "startDate must be smaller than endDate")
    except Exception as e:
        return ResponseObject(False, "Dates are invalid" + e)
    if not configurationName or not id:
        return ResponseObject(False, "Please provide configurationName and id")
    fp, p = WireguardConfigurations.get(configurationName).searchPeer(id)
    if fp:
        return ResponseObject(data=p.getTraffics(interval, startDate, endDate))
    return ResponseObject(False, "Peer does not exist")

@app.get(f'{APP_PREFIX}/api/getDashboardTheme')
def API_getDashboardTheme():
    return ResponseObject(data=DashboardConfig.GetConfig("Server", "dashboard_theme")[1])

@app.get(f'{APP_PREFIX}/api/getDashboardVersion')
def API_getDashboardVersion():
    return ResponseObject(data=DashboardConfig.GetConfig("Server", "version")[1])

@app.post(f'{APP_PREFIX}/api/savePeerScheduleJob')
def API_savePeerScheduleJob():
    data = request.json
    if "Job" not in data.keys():
        return ResponseObject(False, "Please specify job")
    job: dict = data['Job']
    if "Peer" not in job.keys() or "Configuration" not in job.keys():
        return ResponseObject(False, "Please specify peer and configuration")
    configuration = WireguardConfigurations.get(job['Configuration'])
    if configuration is None:
        return ResponseObject(False, "Configuration does not exist")
    f, fp = configuration.searchPeer(job['Peer'])
    if not f:
        return ResponseObject(False, "Peer does not exist")
    
    
    s, p = AllPeerJobs.saveJob(PeerJob(
        job['JobID'], job['Configuration'], job['Peer'], job['Field'], job['Operator'], job['Value'],
        job['CreationDate'], job['ExpireDate'], job['Action']))
    if s:
        return ResponseObject(s, data=p)
    return ResponseObject(s, message=p)

@app.post(f'{APP_PREFIX}/api/deletePeerScheduleJob')
def API_deletePeerScheduleJob():
    data = request.json
    if "Job" not in data.keys():
        return ResponseObject(False, "Please specify job")
    job: dict = data['Job']
    if "Peer" not in job.keys() or "Configuration" not in job.keys():
        return ResponseObject(False, "Please specify peer and configuration")
    configuration = WireguardConfigurations.get(job['Configuration'])
    if configuration is None:
        return ResponseObject(False, "Configuration does not exist")
    # f, fp = configuration.searchPeer(job['Peer'])
    # if not f:
    #     return ResponseObject(False, "Peer does not exist")

    s, p = AllPeerJobs.deleteJob(PeerJob(
        job['JobID'], job['Configuration'], job['Peer'], job['Field'], job['Operator'], job['Value'],
        job['CreationDate'], job['ExpireDate'], job['Action']))
    if s:
        return ResponseObject(s)
    return ResponseObject(s, message=p)

@app.get(f'{APP_PREFIX}/api/getPeerScheduleJobLogs/<configName>')
def API_getPeerScheduleJobLogs(configName):
    if configName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration does not exist")
    data = request.args.get("requestAll")
    requestAll = False
    if data is not None and data == "true":
        requestAll = True
    return ResponseObject(data=AllPeerJobs.getPeerJobLogs(configName))

'''
File Download
'''
@app.get(f'{APP_PREFIX}/fileDownload')
def API_download():
    file = request.args.get('file')
    if file is None or len(file) == 0:
        return ResponseObject(False, "Please specify a file")
    if os.path.exists(os.path.join('download', file)):
        return send_file(os.path.join('download', file), as_attachment=True)
    else:
        return ResponseObject(False, "File does not exist")


'''
Tools
'''

@app.get(f'{APP_PREFIX}/api/ping/getAllPeersIpAddress')
def API_ping_getAllPeersIpAddress():
    ips = {}
    for c in WireguardConfigurations.values():
        cips = {}
        for p in c.Peers:
            allowed_ip = p.allowed_ip.replace(" ", "").split(",")
            parsed = []
            for x in allowed_ip:
                try:
                    ip = ipaddress.ip_network(x, strict=False)
                except ValueError as e:
                    app.logger.error(f"Failed to parse IP address of {p.id} - {c.Name}")
                if len(list(ip.hosts())) == 1:
                    parsed.append(str(ip.hosts()[0]))
            endpoint = p.endpoint.replace(" ", "").replace("(none)", "")
            if len(p.name) > 0:
                cips[f"{p.name} - {p.id}"] = {
                    "allowed_ips": parsed,
                    "endpoint": endpoint
                }
            else:
                cips[f"{p.id}"] = {
                    "allowed_ips": parsed,
                    "endpoint": endpoint
                }
        ips[c.Name] = cips
    return ResponseObject(data=ips)

import requests

@app.get(f'{APP_PREFIX}/api/ping/execute')
def API_ping_execute():
    if "ipAddress" in request.args.keys() and "count" in request.args.keys():
        ip = request.args['ipAddress']
        count = request.args['count']
        try:
            if ip is not None and len(ip) > 0 and count is not None and count.isnumeric():
                result = ping(ip, count=int(count), source=None)
                data = {
                    "address": result.address,
                    "is_alive": result.is_alive,
                    "min_rtt": result.min_rtt,
                    "avg_rtt": result.avg_rtt,
                    "max_rtt": result.max_rtt,
                    "package_sent": result.packets_sent,
                    "package_received": result.packets_received,
                    "package_loss": result.packet_loss,
                    "geo": None
                }
                try:
                    r = requests.get(f"http://ip-api.com/json/{result.address}?field=city")
                    data['geo'] = r.json()
                except Exception as e:
                    pass
                return ResponseObject(data=data)
            return ResponseObject(False, "Please specify an IP Address (v4/v6)")
        except Exception as exp:
            return ResponseObject(False, exp)
    return ResponseObject(False, "Please provide ipAddress and count")


@app.get(f'{APP_PREFIX}/api/traceroute/execute')
def API_traceroute_execute():
    if "ipAddress" in request.args.keys() and len(request.args.get("ipAddress")) > 0:
        ipAddress = request.args.get('ipAddress')
        try:
            tracerouteResult = traceroute(ipAddress, timeout=1, max_hops=64)
            result = []
            for hop in tracerouteResult:
                if len(result) > 1:
                    skipped = False
                    for i in range(result[-1]["hop"] + 1, hop.distance):
                        result.append(
                            {
                                "hop": i,
                                "ip": "*",
                                "avg_rtt": "*",
                                "min_rtt": "*",
                                "max_rtt": "*"
                            }
                        )
                        skip = True
                    if skipped: continue
                result.append(
                    {
                        "hop": hop.distance,
                        "ip": hop.address,
                        "avg_rtt": hop.avg_rtt,
                        "min_rtt": hop.min_rtt,
                        "max_rtt": hop.max_rtt
                    })
            try:
                r = requests.post(f"http://ip-api.com/batch?fields=city,country,lat,lon,query",
                                  data=json.dumps([x['ip'] for x in result]))
                d = r.json()
                for i in range(len(result)):
                    result[i]['geo'] = d[i]  
            except Exception as e:
                return ResponseObject(data=result, message="Failed to request IP address geolocation")
            return ResponseObject(data=result)
        except Exception as exp:
            return ResponseObject(False, exp)
    else:
        return ResponseObject(False, "Please provide ipAddress")

@app.get(f'{APP_PREFIX}/api/getDashboardUpdate')
def API_getDashboardUpdate():
    import urllib.request as req
    try:
        r = req.urlopen("https://api.github.com/repos/WGDashboard/WGDashboard/releases/latest", timeout=5).read()
        data = dict(json.loads(r))
        tagName = data.get('tag_name')
        htmlUrl = data.get('html_url')
        if tagName is not None and htmlUrl is not None:
            if version.parse(tagName) > version.parse(DashboardConfig.DashboardVersion):
                return ResponseObject(message=f"{tagName} is now available for update!", data=htmlUrl)
            else:
                return ResponseObject(message="You're on the latest version")
        return ResponseObject(False)
    except Exception as e:
        return ResponseObject(False, f"Request to GitHub API failed.")

'''
Sign Up
'''

@app.get(f'{APP_PREFIX}/api/isTotpEnabled')
def API_isTotpEnabled():
    return (
        ResponseObject(data=DashboardConfig.GetConfig("Account", "enable_totp")[1] and DashboardConfig.GetConfig("Account", "totp_verified")[1]))


@app.get(f'{APP_PREFIX}/api/Welcome_GetTotpLink')
def API_Welcome_GetTotpLink():
    if not DashboardConfig.GetConfig("Account", "totp_verified")[1]:
        DashboardConfig.SetConfig("Account", "totp_key", pyotp.random_base32(), True)
        return ResponseObject(
            data=pyotp.totp.TOTP(DashboardConfig.GetConfig("Account", "totp_key")[1]).provisioning_uri(
                issuer_name="WGDashboard"))
    return ResponseObject(False)


@app.post(f'{APP_PREFIX}/api/Welcome_VerifyTotpLink')
def API_Welcome_VerifyTotpLink():
    data = request.get_json()
    totp = pyotp.TOTP(DashboardConfig.GetConfig("Account", "totp_key")[1]).now()
    if totp == data['totp']:
        DashboardConfig.SetConfig("Account", "totp_verified", "true")
        DashboardConfig.SetConfig("Account", "enable_totp", "true")
    return ResponseObject(totp == data['totp'])

@app.post(f'{APP_PREFIX}/api/Welcome_Finish')
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
                                                                          "repeatNewPassword": data["repeatNewPassword"],
                                                                          "currentPassword": "admin"
                                                                      })
        if not updateUsername or not updatePassword:
            return ResponseObject(False, f"{updateUsernameErr},{updatePasswordErr}".strip(","))

        DashboardConfig.SetConfig("Other", "welcome_session", False)
    return ResponseObject()

@app.get(f'{APP_PREFIX}/api/locale')
def API_Locale_CurrentLang():    
    return ResponseObject(data=Locale.getLanguage())

@app.get(f'{APP_PREFIX}/api/locale/available')
def API_Locale_Available():
    return ResponseObject(data=Locale.activeLanguages)
        
@app.post(f'{APP_PREFIX}/api/locale/update')
def API_Locale_Update():
    data = request.get_json()
    if 'lang_id' not in data.keys():
        return ResponseObject(False, "Please specify a lang_id")
    Locale.updateLanguage(data['lang_id'])
    return ResponseObject(data=Locale.getLanguage())

@app.get(f'{APP_PREFIX}/api/email/ready')
def API_Email_Ready():
    return ResponseObject(EmailSender.ready())

@app.post(f'{APP_PREFIX}/api/email/send')
def API_Email_Send():
    data = request.get_json()
    if "Receiver" not in data.keys() or "Subject" not in data.keys():
        return ResponseObject(False, "Please at least specify receiver and subject")
    body = data.get('Body', '')
    subject = data.get('Subject','')
    download = None
    if ("ConfigurationName" in data.keys() 
            and "Peer" in data.keys()):
        if data.get('ConfigurationName') in WireguardConfigurations.keys():
            configuration = WireguardConfigurations.get(data.get('ConfigurationName'))
            attachmentName = ""
            if configuration is not None:
                fp, p = configuration.searchPeer(data.get('Peer'))
                if fp:
                    template = Template(body)
                    download = p.downloadPeer()
                    body = template.render(peer=p.toJson(), configurationFile=download)
                    subject = Template(data.get('Subject', '')).render(peer=p.toJson(), configurationFile=download)
                    if data.get('IncludeAttachment', False):
                        u = str(uuid4())
                        attachmentName = f'{u}.conf'
                        with open(os.path.join('./attachments', attachmentName,), 'w+') as f:
                            f.write(download['file'])   
                        
    
    s, m = EmailSender.send(data.get('Receiver'), subject, body,  
                            data.get('IncludeAttachment', False), (attachmentName if download else ''))
    return ResponseObject(s, m)

@app.post(f'{APP_PREFIX}/api/email/preview')
def API_Email_PreviewBody():
    data = request.get_json()
    subject = data.get('Subject', '')
    body = data.get('Body', '')
    
    if ("ConfigurationName" not in data.keys() 
            or "Peer" not in data.keys() or data.get('ConfigurationName') not in WireguardConfigurations.keys()):
        return ResponseObject(False, "Please specify configuration and peer")
    
    configuration = WireguardConfigurations.get(data.get('ConfigurationName'))
    fp, p = configuration.searchPeer(data.get('Peer'))
    if not fp:
        return ResponseObject(False, "Peer does not exist")

    try:
        template = Template(body)
        download = p.downloadPeer()
        return ResponseObject(data={
            "Body": Template(body).render(peer=p.toJson(), configurationFile=download),
            "Subject": Template(subject).render(peer=p.toJson(), configurationFile=download)
        })
    except Exception as e:
        return ResponseObject(False, message=str(e))

@app.get(f'{APP_PREFIX}/api/systemStatus')
def API_SystemStatus():
    return ResponseObject(data=SystemStatus)

@app.get(f'{APP_PREFIX}/api/protocolsEnabled')
def API_ProtocolsEnabled():
    return ResponseObject(data=ProtocolsEnabled())

class Locale:
    def __init__(self):
        self.localePath = './static/locales/'
        self.activeLanguages = {}
        with open(os.path.join(f"{self.localePath}supported_locales.json"), "r") as f:
            self.activeLanguages = sorted(json.loads(''.join(f.readlines())), key=lambda x : x['lang_name'])
        
    def getLanguage(self) -> dict | None:
        currentLanguage = DashboardConfig.GetConfig("Server", "dashboard_language")[1]
        if currentLanguage == "en":
            return None
        if os.path.exists(os.path.join(f"{self.localePath}{currentLanguage}.json")):
            with open(os.path.join(f"{self.localePath}{currentLanguage}.json"), "r") as f:
                return dict(json.loads(''.join(f.readlines())))
        else:
            return None
    
    def updateLanguage(self, lang_id):
        if not os.path.exists(os.path.join(f"{self.localePath}{lang_id}.json")):
            DashboardConfig.SetConfig("Server", "dashboard_language", "en-US")
        else:
            DashboardConfig.SetConfig("Server", "dashboard_language", lang_id)

Locale = Locale()

'''
OIDC Controller
'''
@app.get(f'{APP_PREFIX}/api/oidc/toggle')
def API_OIDC_Toggle():
    data = request.args
    if not data.get('mode'):
        return ResponseObject(False, "Please provide mode")
    mode = data.get('mode')
    if mode == 'Client':
        DashboardConfig.SetConfig("OIDC", "client_enable", 
                                  not DashboardConfig.GetConfig("OIDC", "client_enable")[1])
    elif mode == 'Admin':
        DashboardConfig.SetConfig("OIDC", "admin_enable",
                                  not DashboardConfig.GetConfig("OIDC", "admin_enable")[1])
    else:
        return ResponseObject(False, "Mode does not exist")
    return ResponseObject()

@app.get(f'{APP_PREFIX}/api/oidc/status')
def API_OIDC_Status():
    data = request.args
    if not data.get('mode'):
        return ResponseObject(False, "Please provide mode")
    mode = data.get('mode')
    if mode == 'Client':
        return ResponseObject(data=DashboardConfig.GetConfig("OIDC", "client_enable")[1])
    elif mode == 'Admin':
        return ResponseObject(data=DashboardConfig.GetConfig("OIDC", "admin_enable")[1])
    return ResponseObject(False, "Mode does not exist")

'''
Client Controller
'''

@app.get(f'{APP_PREFIX}/api/clients/toggleStatus')
def API_Clients_ToggleStatus():
    DashboardConfig.SetConfig("Clients", "enable",
                              not DashboardConfig.GetConfig("Clients", "enable")[1])
    return ResponseObject(data=DashboardConfig.GetConfig("Clients", "enable")[1])


@app.get(f'{APP_PREFIX}/api/clients/allClients')
def API_Clients_AllClients():
    return ResponseObject(data=DashboardClients.GetAllClients())

@app.get(f'{APP_PREFIX}/api/clients/allClientsRaw')
def API_Clients_AllClientsRaw():
    return ResponseObject(data=DashboardClients.GetAllClientsRaw())

@app.post(f'{APP_PREFIX}/api/clients/assignClient')
def API_Clients_AssignClient():
    data = request.get_json()
    configurationName = data.get('ConfigurationName')
    id = data.get('Peer')
    client = data.get('ClientID')
    if not all([configurationName, id, client]):
        return ResponseObject(False, "Please provide all required fields")
    if not DashboardClients.GetClient(client):
        return ResponseObject(False, "Client does not exist")
    
    status, data = DashboardClients.AssignClient(configurationName, id, client)
    if not status:
        return ResponseObject(status, message="Client already assiged to this peer")
    
    return ResponseObject(data=data)

@app.post(f'{APP_PREFIX}/api/clients/unassignClient')
def API_Clients_UnassignClient():
    data = request.get_json()
    assignmentID = data.get('AssignmentID')
    if not assignmentID:
        return ResponseObject(False, "Please provide AssignmentID")
    return ResponseObject(status=DashboardClients.UnassignClient(assignmentID))

@app.get(f'{APP_PREFIX}/api/clients/assignedClients')
def API_Clients_AssignedClients():
    data = request.args
    configurationName = data.get('ConfigurationName')
    peerID = data.get('Peer')
    if not all([configurationName, id]):
        return ResponseObject(False, "Please provide all required fields")
    return ResponseObject(
        data=DashboardClients.GetAssignedPeerClients(configurationName, peerID))

@app.get(f'{APP_PREFIX}/api/clients/allConfigurationsPeers')
def API_Clients_AllConfigurationsPeers():
    c = {}
    for (key, val) in WireguardConfigurations.items():
        c[key] = list(map(lambda x : {
            "id": x.id,
            "name": x.name
        }, val.Peers))
    
    return ResponseObject(
        data=c
    )

@app.get(f'{APP_PREFIX}/api/clients/assignedPeers')
def API_Clients_AssignedPeers():
    data = request.args
    clientId = data.get("ClientID")
    if not clientId:
        return ResponseObject(False, "Please provide ClientID")
    if not DashboardClients.GetClient(clientId):
        return ResponseObject(False, "Client does not exist")
    d = DashboardClients.GetClientAssignedPeersGrouped(clientId)
    if d is None:
        return ResponseObject(False, "Client does not exist")
    return ResponseObject(data=d)

@app.post(f'{APP_PREFIX}/api/clients/generatePasswordResetLink')
def API_Clients_GeneratePasswordResetLink():
    data = request.get_json()
    clientId = data.get("ClientID")
    if not clientId:
        return ResponseObject(False, "Please provide ClientID")
    if not DashboardClients.GetClient(clientId):
        return ResponseObject(False, "Client does not exist")
    
    token = DashboardClients.GenerateClientPasswordResetToken(clientId)
    if token:
        return ResponseObject(data=token)
    return ResponseObject(False, "Failed to generate link")

@app.post(f'{APP_PREFIX}/api/clients/updateProfileName')
def API_Clients_UpdateProfile():
    data = request.get_json()
    clientId = data.get("ClientID")
    if not clientId:
        return ResponseObject(False, "Please provide ClientID")
    if not DashboardClients.GetClient(clientId):
        return ResponseObject(False, "Client does not exist")
    
    value = data.get('Name')
    return ResponseObject(status=DashboardClients.UpdateClientProfile(clientId, value))

@app.post(f'{APP_PREFIX}/api/clients/deleteClient')
def API_Clients_DeleteClient():
    data = request.get_json()
    clientId = data.get("ClientID")
    if not clientId:
        return ResponseObject(False, "Please provide ClientID")
    if not DashboardClients.GetClient(clientId):
        return ResponseObject(False, "Client does not exist")
    return ResponseObject(status=DashboardClients.DeleteClient(clientId))   

@app.get(f'{APP_PREFIX}/api/webHooks/getWebHooks')
def API_WebHooks_GetWebHooks():
    return ResponseObject(data=DashboardWebHooks.GetWebHooks())

@app.get(f'{APP_PREFIX}/api/webHooks/createWebHook')
def API_WebHooks_createWebHook():
    return ResponseObject(data=DashboardWebHooks.CreateWebHook().model_dump(
        exclude={'CreationDate'}
    ))

@app.post(f'{APP_PREFIX}/api/webHooks/updateWebHook')
def API_WebHooks_UpdateWebHook():
    data = request.get_json()
    status, msg = DashboardWebHooks.UpdateWebHook(data)
    return ResponseObject(status, msg)

@app.post(f'{APP_PREFIX}/api/webHooks/deleteWebHook')
def API_WebHooks_DeleteWebHook():
    data = request.get_json()
    status, msg = DashboardWebHooks.DeleteWebHook(data)
    return ResponseObject(status, msg)

@app.get(f'{APP_PREFIX}/api/webHooks/getWebHookSessions')
def API_WebHooks_GetWebHookSessions():
    webhookID = request.args.get('WebHookID')
    if not webhookID:
        return ResponseObject(False, "Please provide WebHookID")
    
    webHook = DashboardWebHooks.SearchWebHookByID(webhookID)
    if not webHook:
        return ResponseObject(False, "Webhook does not exist")
    
    return ResponseObject(data=DashboardWebHooks.GetWebHookSessions(webHook))
    

'''
Index Page
'''

@app.get(f'{APP_PREFIX}/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    startThreads()
    DashboardPlugins.startThreads()
    app.run(host=app_ip, debug=False, port=app_port)