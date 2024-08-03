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
import uuid
from datetime import datetime, timedelta
from typing import Any

import bcrypt
# PIP installed library
import ifcfg
import psutil
import pyotp
from flask import Flask, request, render_template, session
from json import JSONEncoder
from flask_cors import CORS

from icmplib import ping, traceroute

# Import other python files
import threading

from flask.json.provider import DefaultJSONProvider

DASHBOARD_VERSION = 'v4.0'
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
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

class ModelEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, 'toJson'):
            return o.toJson()
        else:
            return super(ModelEncoder, self).default(o)


'''
Classes
'''


def ResponseObject(status=True, message=None, data=None) -> Flask.response_class:
    response = Flask.make_response(app, {
        "status": status,
        "message": message,
        "data": data
    })
    response.content_type = "application/json"
    return response


class CustomJsonEncoder(DefaultJSONProvider):
    def __init__(self, app):
        super().__init__(app)

    def default(self, o):
        if isinstance(o, WireguardConfiguration) or isinstance(o, Peer) or isinstance(o, PeerJob) or isinstance(o, Log) or isinstance(o, DashboardAPIKey):
            return o.toJson()
        return super().default(self, o)


app.json = CustomJsonEncoder(app)

class Log:
    def __init__(self, LogID: str, JobID: str, LogDate: str, Status: str, Message: str):
        self.LogID = LogID
        self.JobID = JobID
        self.LogDate = LogDate
        self.Status = Status
        self.Message = Message
    
    def toJson(self):
        return {
            "LogID": self.LogID,
            "JobID": self.JobID,
            "LogDate": self.LogDate,
            "Status": self.Status,
            "Message": self.Message
        }

    def __dict__(self):
        return self.toJson()
    
class Logger:
    def __init__(self):
        self.loggerdb = sqlite3.connect(os.path.join(CONFIGURATION_PATH, 'db', 'wgdashboard_log.db'),
                                     check_same_thread=False)
        self.loggerdb.row_factory = sqlite3.Row
        self.logs:list(Log) = []
        self.loggerdbCursor = self.loggerdb.cursor()
        self.__createLogDatabase()
        
    def __createLogDatabase(self):
        existingTable = self.loggerdbCursor.execute("SELECT name from sqlite_master where type='table'").fetchall()
        existingTable = [t['name'] for t in existingTable]

        if "JobLog" not in existingTable:
            self.loggerdbCursor.execute("CREATE TABLE JobLog (LogID VARCHAR NOT NULL, JobID NOT NULL, LogDate DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now', 'localtime')), Status VARCHAR NOT NULL, Message VARCHAR, PRIMARY KEY (LogID))")
            self.loggerdb.commit()
    def log(self, JobID: str, Status: bool = True, Message: str = "") -> bool:
        try:
            self.loggerdbCursor.execute(f"INSERT INTO JobLog (LogID, JobID, Status, Message) VALUES (?, ?, ?, ?)",
                                        (str(uuid.uuid4()), JobID, Status, Message,))
            self.loggerdb.commit()
        except Exception as e:
            print(e)
            return False
        return True
    
    def getLogs(self, all: bool = False, configName = None) -> list[Log]:
        logs: list[Log] = []
        try:
            allJobs = AllPeerJobs.getAllJobs(configName)
            allJobsID = ", ".join([f"'{x.JobID}'" for x in allJobs])
            table = self.loggerdb.execute(f"SELECT * FROM JobLog WHERE JobID IN ({allJobsID}) ORDER BY LogDate DESC").fetchall()
            self.logs.clear()
            for l in table:
                logs.append(
                    Log(l["LogID"], l["JobID"], l["LogDate"], l["Status"], l["Message"]))
        except Exception as e:
            return logs
        return logs
            
class PeerJob:
    def __init__(self, JobID: str, Configuration: str, Peer: str,
                 Field: str, Operator: str, Value: str, CreationDate: datetime, ExpireDate: datetime, Action: str):
        self.Action = Action
        self.ExpireDate = ExpireDate
        self.CreationDate = CreationDate
        self.Value = Value
        self.Operator = Operator
        self.Field = Field
        self.Configuration = Configuration
        self.Peer = Peer
        self.JobID = JobID

    def toJson(self):
        return {
            "JobID": self.JobID,
            "Configuration": self.Configuration,
            "Peer": self.Peer,
            "Field": self.Field,
            "Operator": self.Operator,
            "Value": self.Value,
            "CreationDate": self.CreationDate,
            "ExpireDate": self.ExpireDate,
            "Action": self.Action
        }

    def __dict__(self):
        return self.toJson()

class PeerJobs:

    def __init__(self):
        self.Jobs: list[PeerJob] = []
        self.jobdb = sqlite3.connect(os.path.join(CONFIGURATION_PATH, 'db', 'wgdashboard_job.db'),
                                     check_same_thread=False)
        self.jobdb.row_factory = sqlite3.Row
        self.jobdbCursor = self.jobdb.cursor()
        self.__createPeerJobsDatabase()
        self.__getJobs()

    def __getJobs(self):
        self.Jobs.clear()
        jobs = self.jobdbCursor.execute("SELECT * FROM PeerJobs WHERE ExpireDate IS NULL").fetchall()
        for job in jobs:
            self.Jobs.append(PeerJob(
                job['JobID'], job['Configuration'], job['Peer'], job['Field'], job['Operator'], job['Value'],
                job['CreationDate'], job['ExpireDate'], job['Action']))
    
    def getAllJobs(self, configuration: str = None):
        if configuration is not None:
            jobs = self.jobdbCursor.execute(
                f"SELECT * FROM PeerJobs WHERE Configuration = ?", (configuration, )).fetchall()
            j = []
            for job in jobs:
                j.append(PeerJob(
                    job['JobID'], job['Configuration'], job['Peer'], job['Field'], job['Operator'], job['Value'],
                    job['CreationDate'], job['ExpireDate'], job['Action']))
            return j
        return []

    def __createPeerJobsDatabase(self):
        existingTable = self.jobdbCursor.execute("SELECT name from sqlite_master where type='table'").fetchall()
        existingTable = [t['name'] for t in existingTable]

        if "PeerJobs" not in existingTable:
            self.jobdbCursor.execute('''
            CREATE TABLE PeerJobs (JobID VARCHAR NOT NULL, Configuration VARCHAR NOT NULL, Peer VARCHAR NOT NULL,
            Field VARCHAR NOT NULL, Operator VARCHAR NOT NULL, Value VARCHAR NOT NULL, CreationDate DATETIME,
            ExpireDate DATETIME, Action VARCHAR NOT NULL, PRIMARY KEY (JobID))
            ''')
            self.jobdb.commit()

    def toJson(self):
        return [x.toJson() for x in self.Jobs]

    def searchJob(self, Configuration: str, Peer: str):
        return list(filter(lambda x: x.Configuration == Configuration and x.Peer == Peer, self.Jobs))

    def saveJob(self, Job: PeerJob) -> tuple[bool, list] | tuple[bool, str]:
        try:
            if (len(str(Job.CreationDate))) == 0:
                self.jobdbCursor.execute('''
                INSERT INTO PeerJobs VALUES (?, ?, ?, ?, ?, ?, strftime('%Y-%m-%d %H:%M:%S','now'), NULL, ?)
                ''', (Job.JobID, Job.Configuration, Job.Peer, Job.Field, Job.Operator, Job.Value, Job.Action,))
                JobLogger.log(Job.JobID, Message=f"Job is created if {Job.Field} {Job.Operator} {Job.Value} then {Job.Action}")
                
            else:
                currentJob = self.jobdbCursor.execute('SELECT * FROM PeerJobs WHERE JobID = ?', (Job.JobID, )).fetchone()
                if currentJob is not None:
                    self.jobdbCursor.execute('''
                        UPDATE PeerJobs SET Field = ?, Operator = ?, Value = ?, Action = ? WHERE JobID = ?
                        ''', (Job.Field, Job.Operator, Job.Value, Job.Action, Job.JobID))
                    JobLogger.log(Job.JobID, 
                                  Message=f"Job is updated from if {currentJob['Field']} {currentJob['Operator']} {currentJob['value']} then {currentJob['Action']}; to if {Job.Field} {Job.Operator} {Job.Value} then {Job.Action}")
            self.jobdb.commit()
            self.__getJobs()
        
            return True, list(
                filter(lambda x: x.Configuration == Job.Configuration and x.Peer == Job.Peer and x.JobID == Job.JobID,
                       self.Jobs))
        except Exception as e:
            return False, str(e)

    def deleteJob(self, Job: PeerJob) -> tuple[bool, list] | tuple[bool, str]:
        try:
            if (len(str(Job.CreationDate))) == 0:
                return False, "Job does not exist"
            self.jobdbCursor.execute('''
                UPDATE PeerJobs SET ExpireDate = strftime('%Y-%m-%d %H:%M:%S','now') WHERE JobID = ?
            ''', (Job.JobID,))
            self.jobdb.commit()
            JobLogger.log(Job.JobID, Message=f"Job is removed due to being deleted or finshed.")
            self.__getJobs()
            return True, list(
                filter(lambda x: x.Configuration == Job.Configuration and x.Peer == Job.Peer and x.JobID == Job.JobID,
                       self.Jobs))
        except Exception as e:
            return False, str(e)

    def runJob(self):
        needToDelete = []
        for job in self.Jobs:
            print(job.toJson())
            c = WireguardConfigurations.get(job.Configuration)
            if c is not None:
                f, fp = c.searchPeer(job.Peer)
                if f:
                    if job.Field in ["total_receive", "total_sent", "total_data"]:
                        s = job.Field.split("_")[1]
                        x: float = getattr(fp, f"total_{s}") + getattr(fp, f"cumu_{s}")
                        y: float = float(job.Value)
                    else:
                        x: datetime = datetime.now()
                        y: datetime = datetime.strptime(job.Value, "%Y-%m-%dT%H:%M")
                        

                    runAction: bool = self.__runJob_Compare(x, y, job.Operator)
                    print("Running Job:" + str(runAction) + "\n")
                    if runAction:
                        s = False
                        if job.Action == "restrict":
                            s = c.restrictPeers([fp.id]).get_json()
                        elif job.Action == "delete":
                            s = c.deletePeers([fp.id]).get_json()
                
                        if s['status'] is True:
                            JobLogger.log(job.JobID, s["status"], 
                                          f"Peer {fp.id} from {c.Name} is successfully {job.Action}ed."
                            )
                            needToDelete.append(job)
                        else:
                            JobLogger.log(job.JobID, s["status"],
                                          f"Peer {fp.id} from {c.Name} failed {job.Action}ed."
                            )
        print(f'''[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Peer Job Schedule: Ran {len(needToDelete)} job(s)''')
        for j in needToDelete:
            self.deleteJob(j)

    def __runJob_Compare(self, x: float | datetime, y: float | datetime, operator: str):
        if operator == "eq":
            return x == y
        if operator == "neq":
            return x != y
        if operator == "lgt":
            return x > y
        if operator == "lst":
            return x < y

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

        self.Peers: list[Peer] = []
        # Create tables in database
        self.__createDatabase()
        self.getPeersList()

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

    def __getRestrictedPeers(self):
        self.RestrictedPeers = []
        restricted = cursor.execute("SELECT * FROM %s_restrict_access" % self.Name).fetchall()
        for i in restricted:
            self.RestrictedPeers.append(Peer(i, self))

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
                            self.Peers.append(Peer(newPeer, self))
                        else:
                            cursor.execute("UPDATE %s SET allowed_ip = ? WHERE id = ?" % self.Name,
                                           (i.get("AllowedIPs", "N/A"), i['PublicKey'],))
                            sqldb.commit()
                            self.Peers.append(Peer(checkIfExist, self))
            except ValueError:
                pass

    def searchPeer(self, publicKey):
        for i in self.Peers:
            if i.id == publicKey:
                return True, i
        return False, None

    def allowAccessPeers(self, listOfPublicKeys):
        # numOfAllowedPeers = 0
        # numOfFailedToAllowPeers = 0
        for i in listOfPublicKeys:
            p = cursor.execute("SELECT * FROM %s_restrict_access WHERE id = ?" % self.Name, (i,)).fetchone()
            if p is not None:
                cursor.execute("INSERT INTO %s SELECT * FROM %s_restrict_access WHERE id = ?"
                               % (self.Name, self.Name,), (p['id'],))
                cursor.execute("DELETE FROM %s_restrict_access WHERE id = ?"
                               % self.Name, (p['id'],))
                subprocess.check_output(f"wg set {self.Name} peer {p['id']} allowed-ips {p['allowed_ip']}",
                                        shell=True, stderr=subprocess.STDOUT)
            else:
                return ResponseObject(False, "Failed to allow access of peer " + i)
        if not self.__wgSave():
            return ResponseObject(False, "Failed to save configuration through WireGuard")

        self.__getPeers()
        return ResponseObject(True, "Allow access successfully!")

    def restrictPeers(self, listOfPublicKeys):
        numOfRestrictedPeers = 0
        numOfFailedToRestrictPeers = 0
        for p in listOfPublicKeys:
            found, pf = self.searchPeer(p)
            if found:
                try:
                    subprocess.check_output(f"wg set {self.Name} peer {pf.id} remove",
                                            shell=True, stderr=subprocess.STDOUT)
                    cursor.execute("INSERT INTO %s_restrict_access SELECT * FROM %s WHERE id = ?" %
                                   (self.Name, self.Name,), (pf.id,))
                    cursor.execute("UPDATE %s_restrict_access SET status = 'stopped' WHERE id = ?" %
                                   (self.Name,), (pf.id,))
                    cursor.execute("DELETE FROM %s WHERE id = ?" % self.Name, (pf.id,))
                    numOfRestrictedPeers += 1
                except Exception as e:
                    numOfFailedToRestrictPeers += 1

        if not self.__wgSave():
            return ResponseObject(False, "Failed to save configuration through WireGuard")

        self.__getPeers()

        if numOfRestrictedPeers == len(listOfPublicKeys):
            return ResponseObject(True, f"Restricted {numOfRestrictedPeers} peer(s)")
        return ResponseObject(False,
                              f"Restricted {numOfRestrictedPeers} peer(s) successfully. Failed to restrict {numOfFailedToRestrictPeers} peer(s)")
        pass

    def deletePeers(self, listOfPublicKeys):
        numOfDeletedPeers = 0
        numOfFailedToDeletePeers = 0
        for p in listOfPublicKeys:
            found, pf = self.searchPeer(p)
            if found:
                try:
                    subprocess.check_output(f"wg set {self.Name} peer {pf.id} remove",
                                            shell=True, stderr=subprocess.STDOUT)
                    cursor.execute("DELETE FROM %s WHERE id = ?" % self.Name, (pf.id,))
                    numOfDeletedPeers += 1
                except Exception as e:
                    numOfFailedToDeletePeers += 1

        if not self.__wgSave():
            return ResponseObject(False, "Failed to save configuration through WireGuard")

        self.__getPeers()

        if numOfDeletedPeers == len(listOfPublicKeys):
            return ResponseObject(True, f"Deleted {numOfDeletedPeers} peer(s)")
        return ResponseObject(False,
                              f"Deleted {numOfDeletedPeers} peer(s) successfully. Failed to delete {numOfFailedToDeletePeers} peer(s)")

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

    def __wgSave(self) -> tuple[bool, str] | tuple[bool, None]:
        try:
            subprocess.check_output(f"wg-quick save {self.Name}", shell=True, stderr=subprocess.STDOUT)
            return True, None
        except subprocess.CalledProcessError as e:
            return False, str(e)

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

                        _, p = self.searchPeer(data_usage[i][0])
                        if p.total_receive != round(total_receive, 4) or p.total_sent != round(total_sent, 4):
                            cursor.execute(
                                "UPDATE %s SET total_receive = ?, total_sent = ?, total_data = ? WHERE id = ?"
                                % self.Name, (round(total_receive, 4), round(total_sent, 4),
                                              round(total_receive + total_sent, 4), data_usage[i][0],))
                        now = datetime.now()
                        now_string = now.strftime("%d/%m/%Y %H:%M:%S")
                        # cursor.execute(f'''
                        #             INSERT INTO %s_transfer
                        #                 (id, total_receive, total_sent, total_data,
                        #                 cumu_receive, cumu_sent, cumu_data, time)
                        #                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        #         ''' % self.Name, (data_usage[i][0], round(total_receive, 4), round(total_sent, 4),
                        #                           round(total_receive + total_sent, 4), round(cumulative_receive, 4),
                        #                           round(cumulative_sent, 4),
                        #                           round(cumulative_sent + cumulative_receive, 4), now_string,))
                        # sqldb.commit()
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

    def getPeersList(self):
        self.__getPeers()
        return self.Peers

    def getRestrictedPeersList(self) -> list:
        self.__getRestrictedPeers()
        return self.RestrictedPeers

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

class Peer:
    def __init__(self, tableData, configuration: WireguardConfiguration):
        self.configuration = configuration
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
        self.jobs: list[PeerJob] = []
        self.getJobs()

    def toJson(self):
        self.getJobs()
        return self.__dict__

    def __repr__(self):
        return str(self.toJson())

    def updatePeer(self, name: str, private_key: str,
                   preshared_key: str,
                   dns_addresses: str, allowed_ip: str, endpoint_allowed_ip: str, mtu: int,
                   keepalive: int) -> ResponseObject:

        existingAllowedIps = [item for row in list(
            map(lambda x: [q.strip() for q in x.split(',')],
                map(lambda y: y.allowed_ip,
                    list(filter(lambda k: k.id != self.id, self.configuration.getPeersList()))))) for item in row]

        if allowed_ip in existingAllowedIps:
            return ResponseObject(False, "Allowed IP already taken by another peer.")
        if not _checkIPWithRange(endpoint_allowed_ip):
            return ResponseObject(False, f"Endpoint Allowed IPs format is incorrect.")
        if len(dns_addresses) > 0 and not _checkDNS(dns_addresses):
            return ResponseObject(False, f"DNS format is incorrect.")
        if mtu < 0 or mtu > 1460:
            return ResponseObject(False, "MTU format is not correct.")
        if keepalive < 0:
            return ResponseObject(False, "Persistent Keepalive format is not correct.")
        if len(private_key) > 0:
            pubKey = _generatePublicKey(private_key)
            if not pubKey[0] or pubKey[1] != self.id:
                return ResponseObject(False, "Private key does not match with the public key.")
        try:
            if len(preshared_key) > 0:
                rd = random.Random()
                uid = uuid.UUID(int=rd.getrandbits(128), version=4)
                with open(f"{uid}", "w+") as f:
                    f.write(preshared_key)
                updatePsk = subprocess.check_output(
                    f"wg set {self.configuration.Name} peer {self.id} preshared-key {uid}",
                    shell=True, stderr=subprocess.STDOUT)
                os.remove(str(uid))
                if len(updatePsk.decode().strip("\n")) != 0:
                    return ResponseObject(False,
                                          "Update peer failed when updating preshared key")
            updateAllowedIp = subprocess.check_output(
                f'wg set {self.configuration.Name} peer {self.id} allowed-ips "{allowed_ip.replace(" ", "")}"',
                shell=True, stderr=subprocess.STDOUT)
            if len(updateAllowedIp.decode().strip("\n")) != 0:
                return ResponseObject(False,
                                      "Update peer failed when updating allowed IPs")
            saveConfig = subprocess.check_output(f"wg-quick save {self.configuration.Name}",
                                                 shell=True, stderr=subprocess.STDOUT)
            if f"wg showconf {self.configuration.Name}" not in saveConfig.decode().strip('\n'):
                return ResponseObject(False,
                                      "Update peer failed when saving the configuration.")
            cursor.execute(
                '''UPDATE %s SET name = ?, private_key = ?, DNS = ?, endpoint_allowed_ip = ?, mtu = ?, 
                keepalive = ?, preshared_key = ? WHERE id = ?''' % self.configuration.Name,
                (name, private_key, dns_addresses, endpoint_allowed_ip, mtu,
                 keepalive, preshared_key, self.id,)
            )
            return ResponseObject()
        except subprocess.CalledProcessError as exc:
            return ResponseObject(False, exc.output.decode("UTF-8").strip())

    def downloadPeer(self) -> dict[str, str]:
        filename = self.name
        if len(filename) == 0:
            filename = "UntitledPeer"
        filename = "".join(filename.split(' '))
        filename = f"{filename}_{self.configuration.Name}"
        illegal_filename = [".", ",", "/", "?", "<", ">", "\\", ":", "*", '|' '\"', "com1", "com2", "com3",
                            "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4",
                            "lpt5", "lpt6", "lpt7", "lpt8", "lpt9", "con", "nul", "prn"]
        for i in illegal_filename:
            filename = filename.replace(i, "")

        peerConfiguration = f'''[Interface]
PrivateKey = {self.private_key}
Address = {self.allowed_ip}
MTU = {str(self.mtu)}
'''
        if len(self.DNS) > 0:
            peerConfiguration += f"DNS = {self.DNS}\n"
        peerConfiguration += f'''
[Peer]
PublicKey = {self.configuration.PublicKey}
AllowedIPs = {self.endpoint_allowed_ip}
Endpoint = {DashboardConfig.GetConfig("Peers", "remote_endpoint")[1]}:{self.configuration.ListenPort}
PersistentKeepalive = {str(self.keepalive)}
'''
        if len(self.preshared_key) > 0:
            peerConfiguration += f"PresharedKey = {self.preshared_key}\n"
        return {
            "fileName": filename,
            "file": peerConfiguration
        }

    def getJobs(self):
        self.jobs = AllPeerJobs.searchJob(self.configuration.Name, self.id)
        # print(AllPeerJobs.searchJob(self.configuration.Name, self.id))

# Regex Match
def regex_match(regex, text):
    pattern = re.compile(regex)
    return pattern.search(text) is not None

def iPv46RegexCheck(ip):
    return re.match(
        '((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9a-f]{1,4}:){7}([0-9a-f]{1,4}|:))|(([0-9a-f]{1,4}:){6}(:[0-9a-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9a-f]{1,4}:){5}(((:[0-9a-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9a-f]{1,4}:){4}(((:[0-9a-f]{1,4}){1,3})|((:[0-9a-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){3}(((:[0-9a-f]{1,4}){1,4})|((:[0-9a-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){2}(((:[0-9a-f]{1,4}){1,5})|((:[0-9a-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9a-f]{1,4}:){1}(((:[0-9a-f]{1,4}){1,6})|((:[0-9a-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9a-f]{1,4}){1,7})|((:[0-9a-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$))',
        ip)

class DashboardAPIKey:
    def __init__(self, Key: str, CreatedAt: str, ExpiredAt: str):
        self.Key = Key
        self.CreatedAt = CreatedAt
        self.ExpiredAt = ExpiredAt
    
    def toJson(self):
        return self.__dict__

class DashboardConfig:

    def __init__(self):
        if not os.path.exists(DASHBOARD_CONF):
            open(DASHBOARD_CONF, "x")
        self.__config = configparser.ConfigParser(strict=False)
        self.__config.read_file(open(DASHBOARD_CONF, "r+"))
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
                "dashboard_theme": "dark",
                "dashboard_api_key": "false"
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
        self.__createAPIKeyTable()
        self.DashboardAPIKeys = self.__getAPIKeys()
    
    def __createAPIKeyTable(self):
        existingTable = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = 'DashboardAPIKeys'").fetchall()
        if len(existingTable) == 0:
            cursor.execute("CREATE TABLE DashboardAPIKeys (Key VARCHAR NOT NULL PRIMARY KEY, CreatedAt DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')), ExpiredAt VARCHAR)")
            sqldb.commit()
    
    def __getAPIKeys(self) -> list[DashboardAPIKey]:
        keys = cursor.execute("SELECT * FROM DashboardAPIKeys WHERE ExpiredAt IS NULL OR ExpiredAt > datetime('now', 'localtime') ORDER BY CreatedAt DESC").fetchall()
        fKeys = []
        for k in keys:
            fKeys.append(DashboardAPIKey(*k))
        return fKeys
    
    def createAPIKeys(self, ExpiredAt = None):
        newKey = secrets.token_urlsafe(32)
        cursor.execute('INSERT INTO DashboardAPIKeys (Key, ExpiredAt) VALUES (?, ?)', (newKey, ExpiredAt,))
        sqldb.commit()
        self.DashboardAPIKeys = self.__getAPIKeys()
        
    def deleteAPIKey(self, key):
        cursor.execute("UPDATE DashboardAPIKeys SET ExpiredAt = datetime('now', 'localtime') WHERE Key = ?", (key, ))
        sqldb.commit()
        self.DashboardAPIKeys = self.__getAPIKeys()
    
    
    
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
        return bcrypt.hashpw(plainTextPassword.encode("utf-8"), bcrypt.gensalt())

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


def _generatePublicKey(privateKey) -> tuple[bool, str] | tuple[bool, None]:
    try:
        publicKey = subprocess.check_output(f"wg pubkey", input=privateKey.encode(), shell=True,
                                            stderr=subprocess.STDOUT)
        return True, publicKey.decode().strip('\n')
    except subprocess.CalledProcessError:
        return False, None


def _generatePrivateKey() -> [bool, str]:
    try:
        publicKey = subprocess.check_output(f"wg genkey", shell=True,
                                            stderr=subprocess.STDOUT)
        return True, publicKey.decode().strip('\n')
    except subprocess.CalledProcessError:
        return False, None


def _getWireguardConfigurationAvailableIP(configName: str) -> tuple[bool, list[str]] | tuple[bool, None]:
    if configName not in WireguardConfigurations.keys():
        return False, None
    configuration = WireguardConfigurations[configName]
    if len(configuration.Address) > 0:
        address = configuration.Address.split(',')
        print(address)
        existedAddress = []
        availableAddress = []
        for p in configuration.Peers:
            if len(p.allowed_ip) > 0:
                add = p.allowed_ip.split(',')
                for i in add:
                    a, c = i.split('/')
                    existedAddress.append(ipaddress.ip_address(a.replace(" ", "")))
        for i in address:
            addressSplit, cidr = i.split('/')
            existedAddress.append(ipaddress.ip_address(addressSplit.replace(" ", "")))
        for i in address:
            network = ipaddress.ip_network(i.replace(" ", ""), False)
            count = 0
            for h in network.hosts():
                if h not in existedAddress:
                    availableAddress.append(ipaddress.ip_network(h).compressed)
                    count += 1
                    if network.version == 6 and count > 255:
                        break
        return True, availableAddress

    return False, None


'''
API Routes
'''

@app.before_request
def auth_req():
    authenticationRequired = DashboardConfig.GetConfig("Server", "auth_req")[1]
    d = request.headers
    if authenticationRequired:
        apiKey = d.get('wg-dashboard-apikey')
        apiKeyEnabled = DashboardConfig.GetConfig("Server", "dashboard_api_key")[1]
        if apiKey is not None and len(apiKey) > 0 and apiKeyEnabled:
            apiKeyExist = len(list(filter(lambda x : x.Key == apiKey, DashboardConfig.DashboardAPIKeys))) == 1
            if not apiKeyExist:
                response = Flask.make_response(app, {
                    "status": False,
                    "message": "API Key does not exist",
                    "data": None
                })
                response.content_type = "application/json"
                response.status_code = 401
                return response
        else:
            if ('/static/' not in request.path and "username" not in session and "/" != request.path
                    and "validateAuthentication" not in request.path and "authenticate" not in request.path
                    and "getDashboardConfiguration" not in request.path and "getDashboardTheme" not in request.path
                    and "isTotpEnabled" not in request.path
            ):
                response = Flask.make_response(app, {
                    "status": False,
                    "message": "Unauthorized access.",
                    "data": None
                })
                response.content_type = "application/json"
                response.status_code = 401
                return response


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

@app.route('/api/getDashboardAPIKeys', methods=['GET'])
def API_getDashboardAPIKeys():
    if DashboardConfig.GetConfig('Server', 'dashboard_api_key'):
        return ResponseObject(data=DashboardConfig.DashboardAPIKeys)
    return ResponseObject(False, "Dashboard API Keys function is disbaled")

@app.route('/api/newDashboardAPIKey', methods=['POST'])
def API_newDashboardAPIKey():
    data = request.get_json()
    if DashboardConfig.GetConfig('Server', 'dashboard_api_key'):
        try:
            if data['neverExpire']:
                expiredAt = None
            else:
                expiredAt = datetime.strptime(data['ExpiredAt'], '%Y-%m-%dT%H:%M:%S')
            DashboardConfig.createAPIKeys(expiredAt)
            return ResponseObject(True, data=DashboardConfig.DashboardAPIKeys)
        except Exception as e:
            return ResponseObject(False, str(e))
    return ResponseObject(False, "Dashboard API Keys function is disbaled")

@app.route('/api/deleteDashboardAPIKey', methods=['POST'])
def API_deleteDashboardAPIKey():
    data = request.get_json()
    if DashboardConfig.GetConfig('Server', 'dashboard_api_key'):
        if len(data['Key']) > 0 and len(list(filter(lambda x : x.Key == data['Key'], DashboardConfig.DashboardAPIKeys))) > 0:
            DashboardConfig.deleteAPIKey(data['Key'])
            return ResponseObject(True, data=DashboardConfig.DashboardAPIKeys)
    return ResponseObject(False, "Dashboard API Keys function is disbaled")
    

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
        mtu = data['mtu']
        keepalive = data['keepalive']
        wireguardConfig = WireguardConfigurations[configName]
        foundPeer, peer = wireguardConfig.searchPeer(id)
        if foundPeer:
            return peer.updatePeer(name, private_key, preshared_key, dns_addresses,
                                   allowed_ip, endpoint_allowed_ip, mtu, keepalive)
    return ResponseObject(False, "Peer does not exist")


@app.route('/api/deletePeers/<configName>', methods=['POST'])
def API_deletePeers(configName: str) -> ResponseObject:
    data = request.get_json()
    peers = data['peers']
    if configName in WireguardConfigurations.keys():
        if len(peers) == 0:
            return ResponseObject(False, "Please specify more than one peer")
        configuration = WireguardConfigurations.get(configName)
        return configuration.deletePeers(peers)

    return ResponseObject(False, "Configuration does not exist")


@app.route('/api/restrictPeers/<configName>', methods=['POST'])
def API_restrictPeers(configName: str) -> ResponseObject:
    data = request.get_json()
    peers = data['peers']
    if configName in WireguardConfigurations.keys():
        if len(peers) == 0:
            return ResponseObject(False, "Please specify more than one peer")
        configuration = WireguardConfigurations.get(configName)
        return configuration.restrictPeers(peers)
    return ResponseObject(False, "Configuration does not exist")


@app.route('/api/allowAccessPeers/<configName>', methods=['POST'])
def API_allowAccessPeers(configName: str) -> ResponseObject:
    data = request.get_json()
    peers = data['peers']
    if configName in WireguardConfigurations.keys():
        if len(peers) == 0:
            return ResponseObject(False, "Please specify more than one peer")
        configuration = WireguardConfigurations.get(configName)
        return configuration.allowAccessPeers(peers)
    return ResponseObject(False, "Configuration does not exist")


@app.route('/api/addPeers/<configName>', methods=['POST'])
def API_addPeers(configName):
    data = request.get_json()
    bulkAdd = data['bulkAdd']
    bulkAddAmount = data['bulkAddAmount']
    public_key = data['public_key']
    allowed_ips = data['allowed_ips']
    endpoint_allowed_ip = data['endpoint_allowed_ip']
    dns_addresses = data['DNS']
    mtu = data['mtu']
    keep_alive = data['keepalive']
    preshared_key = data['preshared_key']

    if configName in WireguardConfigurations.keys():
        config = WireguardConfigurations.get(configName)
        if (not bulkAdd and (len(public_key) == 0 or len(allowed_ips) == 0)) or len(endpoint_allowed_ip) == 0:
            return ResponseObject(False, "Please fill in all required box.")
        if not config.getStatus():
            return ResponseObject(False,
                                  f"{configName} is not running, please turn on the configuration before adding peers.")
        if bulkAdd:
            if bulkAddAmount < 1:
                return ResponseObject(False, "Please specify amount of peers you want to add")
            availableIps = _getWireguardConfigurationAvailableIP(configName)
            if not availableIps[0]:
                return ResponseObject(False, "No more available IP can assign")
            if bulkAddAmount > len(availableIps[1]):
                return ResponseObject(False,
                                      f"The maximum number of peers can add is {len(availableIps[1])}")

            keyPairs = []
            for i in range(bulkAddAmount):
                key = _generatePrivateKey()[1]
                keyPairs.append([key, _generatePublicKey(key)[1], _generatePrivateKey()[1], availableIps[1][i],
                                 f"{config.Name}_{datetime.now().strftime('%m%d%Y%H%M%S')}_Peer_#_{(i + 1)}"])
            if len(keyPairs) == 0:
                return ResponseObject(False, "Generating key pairs by bulk failed")

            for i in range(bulkAddAmount):
                subprocess.check_output(
                    f"wg set {config.Name} peer {keyPairs[i][1]} allowed-ips {keyPairs[i][3]}",
                    shell=True, stderr=subprocess.STDOUT)
            subprocess.check_output(
                f"wg-quick save {config.Name}", shell=True, stderr=subprocess.STDOUT)
            config.getPeersList()

            for i in range(bulkAddAmount):
                found, peer = config.searchPeer(keyPairs[i][1])
                if found:
                    if not peer.updatePeer(keyPairs[i][4], keyPairs[i][0], preshared_key, dns_addresses,
                                           keyPairs[i][3],
                                           endpoint_allowed_ip, mtu, keep_alive).status:
                        return ResponseObject(False, "Failed to add peers in bulk")

            return ResponseObject()

        else:
            if config.searchPeer(public_key)[0] is True:
                return ResponseObject(False, f"This peer already exist.")
            name = data['name']
            private_key = data['private_key']
            subprocess.check_output(
                f"wg set {config.Name} peer {public_key} allowed-ips {''.join(allowed_ips)}",
                shell=True, stderr=subprocess.STDOUT)
            if len(preshared_key) > 0:
                subprocess.check_output(
                    f"wg set {config.Name} peer {public_key} preshared-key {preshared_key}",
                    shell=True, stderr=subprocess.STDOUT)
            subprocess.check_output(
                f"wg-quick save {config.Name}", shell=True, stderr=subprocess.STDOUT)
            config.getPeersList()
            found, peer = config.searchPeer(public_key)
            if found:
                return peer.updatePeer(name, private_key, preshared_key, dns_addresses, ",".join(allowed_ips),
                                       endpoint_allowed_ip, mtu, keep_alive)

    return ResponseObject(False, "Configuration does not exist")


@app.route("/api/downloadPeer/<configName>")
def API_downloadPeer(configName):
    data = request.args
    if configName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration or peer does not exist")
    configuration = WireguardConfigurations[configName]
    peerFound, peer = configuration.searchPeer(data['id'])
    if len(data['id']) == 0 or not peerFound:
        return ResponseObject(False, "Configuration or peer does not exist")
    return ResponseObject(data=peer.downloadPeer())


@app.route("/api/downloadAllPeers/<configName>")
def API_downloadAllPeers(configName):
    if configName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration or peer does not exist")
    configuration = WireguardConfigurations[configName]
    peerData = []
    untitledPeer = 0
    for i in configuration.Peers:
        file = i.downloadPeer()
        if file["fileName"] == "UntitledPeer_" + configName:
            file["fileName"] = str(untitledPeer) + "_" + file["fileName"]
            untitledPeer += 1
        peerData.append(file)
    return ResponseObject(data=peerData)


@app.route("/api/getAvailableIPs/<configName>")
def API_getAvailableIPs(configName):
    status, ips = _getWireguardConfigurationAvailableIP(configName)
    return ResponseObject(status=status, data=ips)


@app.route('/api/getWireguardConfigurationInfo', methods=["GET"])
def API_getConfigurationInfo():
    configurationName = request.args.get("configurationName")
    if not configurationName or configurationName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Please provide configuration name")
    return ResponseObject(data={
        "configurationInfo": WireguardConfigurations[configurationName],
        "configurationPeers": WireguardConfigurations[configurationName].getPeersList(),
        "configurationRestrictedPeers": WireguardConfigurations[configurationName].getRestrictedPeersList()
    })


@app.route('/api/getDashboardTheme')
def API_getDashboardTheme():
    return ResponseObject(data=DashboardConfig.GetConfig("Server", "dashboard_theme")[1])


@app.route('/api/savePeerScheduleJob/', methods=["POST"])
def API_savePeerScheduleJob():
    data = request.json
    if "Job" not in data.keys() not in WireguardConfigurations.keys():
        return ResponseObject(False, "Please specify job")
    job: dict = data['Job']
    if "Peer" not in job.keys() or "Configuration" not in job.keys():
        return ResponseObject(False, "Please specify peer and configuration")
    configuration = WireguardConfigurations.get(job['Configuration'])
    f, fp = configuration.searchPeer(job['Peer'])
    if not f:
        return ResponseObject(False, "Peer does not exist in this configuration")

    s, p = AllPeerJobs.saveJob(PeerJob(
        job['JobID'], job['Configuration'], job['Peer'], job['Field'], job['Operator'], job['Value'],
        job['CreationDate'], job['ExpireDate'], job['Action']))
    if s:
        return ResponseObject(s, data=p)
    return ResponseObject(s, message=p)


@app.route('/api/deletePeerScheduleJob/', methods=['POST'])
def API_deletePeerScheduleJob():
    data = request.json
    if "Job" not in data.keys() not in WireguardConfigurations.keys():
        return ResponseObject(False, "Please specify job")
    job: dict = data['Job']
    if "Peer" not in job.keys() or "Configuration" not in job.keys():
        return ResponseObject(False, "Please specify peer and configuration")
    configuration = WireguardConfigurations.get(job['Configuration'])
    f, fp = configuration.searchPeer(job['Peer'])
    if not f:
        return ResponseObject(False, "Peer does not exist in this configuration")

    s, p = AllPeerJobs.deleteJob(PeerJob(
        job['JobID'], job['Configuration'], job['Peer'], job['Field'], job['Operator'], job['Value'],
        job['CreationDate'], job['ExpireDate'], job['Action']))
    if s:
        return ResponseObject(s, data=p)
    return ResponseObject(s, message=p)

@app.route('/api/getPeerScheduleJobLogs/<configName>', methods=['GET'])
def API_getPeerScheduleJobLogs(configName):
    if configName not in WireguardConfigurations.keys():
        return ResponseObject(False, "Configuration does not exist")
    data = request.args.get("requestAll")
    requestAll = False
    if data is not None and data == "true":
        requestAll = True
    return ResponseObject(data=JobLogger.getLogs(requestAll, configName))



'''
Tools
'''


@app.route('/api/ping/getAllPeersIpAddress')
def API_ping_getAllPeersIpAddress():
    ips = {}
    for c in WireguardConfigurations.values():
        cips = {}
        for p in c.Peers:
            allowed_ip = p.allowed_ip.replace(" ", "").split(",")
            parsed = []
            for x in allowed_ip:
                ip = ipaddress.ip_network(x, strict=False)
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


@app.route('/api/ping/execute')
def API_ping_execute():
    if "ipAddress" in request.args.keys() and "count" in request.args.keys():
        ip = request.args['ipAddress']
        count = request.args['count']
        try:
            if ip is not None and len(ip) > 0 and count is not None and count.isnumeric():
                result = ping(ip, count=int(count), source=None)

                return ResponseObject(data={
                    "address": result.address,
                    "is_alive": result.is_alive,
                    "min_rtt": result.min_rtt,
                    "avg_rtt": result.avg_rtt,
                    "max_rtt": result.max_rtt,
                    "package_sent": result.packets_sent,
                    "package_received": result.packets_received,
                    "package_loss": result.packet_loss
                })

            return ResponseObject(False, "Please specify an IP Address (v4/v6)")
        except Exception as exp:
            return ResponseObject(False, exp)
    return ResponseObject(False, "Please provide ipAddress and count")


@app.route('/api/traceroute/execute')
def API_traceroute_execute():
    if "ipAddress" in request.args.keys() and len(request.args.get("ipAddress")) > 0:
        ipAddress = request.args.get('ipAddress')
        try:
            tracerouteResult = traceroute(ipAddress)
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
            return ResponseObject(data=result)
        except Exception as exp:
            return ResponseObject(False, exp)
    else:
        return ResponseObject(False, "Please provide ipAddress")


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
        totp = pyotp.TOTP(DashboardConfig.GetConfig("Account", "totp_key")[1]).now()
        print(totp)
        return ResponseObject(totp == data['totp'])
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
                                                                          "repeatNewPassword": data["repeatNewPassword"],
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
    return render_template('index.html')


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


def peerJobScheduleBackgroundThread():
    with app.app_context():
        print(f'''[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Peer Job Schedule: Waiting for 10 Seconds''')
        time.sleep(10)
        while True:
            print(f'''[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Peer Job Schedule: Running''')
            AllPeerJobs.runJob()
            time.sleep(10)


def gunicornConfig():
    _, app_ip = DashboardConfig.GetConfig("Server", "app_ip")
    _, app_port = DashboardConfig.GetConfig("Server", "app_port")
    return app_ip, app_port

global sqldb, cursor, DashboardConfig, WireguardConfigurations, AllPeerJobs, JobLogger

sqldb = sqlite3.connect(os.path.join(CONFIGURATION_PATH, 'db', 'wgdashboard.db'), check_same_thread=False)
sqldb.row_factory = sqlite3.Row
cursor = sqldb.cursor()
DashboardConfig = DashboardConfig()
WireguardConfigurations: dict[str, WireguardConfiguration] = {}
AllPeerJobs: PeerJobs = PeerJobs()
JobLogger: Logger = Logger()
_, app_ip = DashboardConfig.GetConfig("Server", "app_ip")
_, app_port = DashboardConfig.GetConfig("Server", "app_port")
_, WG_CONF_PATH = DashboardConfig.GetConfig("Server", "wg_conf_path")
WireguardConfigurations = _getConfigurationList()
bgThread = threading.Thread(target=backGroundThread)
bgThread.daemon = True
bgThread.start()

scheduleJobThread = threading.Thread(target=peerJobScheduleBackgroundThread)
scheduleJobThread.daemon = True
scheduleJobThread.start()

if __name__ == "__main__":
    app.run(host=app_ip, debug=False, port=app_port)
