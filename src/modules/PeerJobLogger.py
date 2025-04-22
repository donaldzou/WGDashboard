"""
Peer Job Logger
"""
import sqlite3, os, uuid
from .Log import Log

class PeerJobLogger:
    def __init__(self, CONFIGURATION_PATH, AllPeerJobs):
        self.loggerdb = sqlite3.connect(os.path.join(CONFIGURATION_PATH, 'db', 'wgdashboard_log.db'),
                                        check_same_thread=False)
        self.loggerdb.row_factory = sqlite3.Row
        self.logs: list[Log] = []
        self.__createLogDatabase()
        self.AllPeerJobs = AllPeerJobs
    def __createLogDatabase(self):
        with self.loggerdb:
            loggerdbCursor = self.loggerdb.cursor()

            existingTable = loggerdbCursor.execute("SELECT name from sqlite_master where type='table'").fetchall()
            existingTable = [t['name'] for t in existingTable]

            if "JobLog" not in existingTable:
                loggerdbCursor.execute("CREATE TABLE JobLog (LogID VARCHAR NOT NULL, JobID NOT NULL, LogDate DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S','now', 'localtime')), Status VARCHAR NOT NULL, Message VARCHAR, PRIMARY KEY (LogID))")
                if self.loggerdb.in_transaction:
                    self.loggerdb.commit()
    def log(self, JobID: str, Status: bool = True, Message: str = "") -> bool:
        try:
            with self.loggerdb:
                loggerdbCursor = self.loggerdb.cursor()
                loggerdbCursor.execute(f"INSERT INTO JobLog (LogID, JobID, Status, Message) VALUES (?, ?, ?, ?)",
                                       (str(uuid.uuid4()), JobID, Status, Message,))
                if self.loggerdb.in_transaction:
                    self.loggerdb.commit()
        except Exception as e:
            print(f"[WGDashboard] Peer Job Log Error: {str(e)}")
            return False
        return True

    def getLogs(self, all: bool = False, configName = None) -> list[Log]:
        logs: list[Log] = []
        try:
            allJobs = self.AllPeerJobs.getAllJobs(configName)
            allJobsID = ", ".join([f"'{x.JobID}'" for x in allJobs])
            with self.loggerdb:
                loggerdbCursor = self.loggerdb.cursor()
                table = loggerdbCursor.execute(f"SELECT * FROM JobLog WHERE JobID IN ({allJobsID}) ORDER BY LogDate DESC").fetchall()
                self.logs.clear()
                for l in table:
                    logs.append(
                        Log(l["LogID"], l["JobID"], l["LogDate"], l["Status"], l["Message"]))
        except Exception as e:
            return logs
        return logs
