"""
Peer Job Logger
"""
import os, uuid
import sqlalchemy as db
from .Log import Log
from datetime import datetime

class PeerJobLogger:
    def __init__(self, CONFIGURATION_PATH, AllPeerJobs):
        self.engine = db.create_engine(f'sqlite:///{os.path.join(CONFIGURATION_PATH, "db", "wgdashboard_log.db")}')
        self.loggerdb = self.engine.connect()
        self.metadata = db.MetaData()
        self.jobLogTable = db.Table('JobLog', self.metadata,
                                    db.Column('LogID', db.VARCHAR, nullable=False, primary_key=True),
                                    db.Column('JobID', db.VARCHAR, nullable=False),
                                    db.Column('LogDate', db.DATETIME, 
                                              server_default=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                    db.Column('Status', db.VARCHAR, nullable=False),
                                    db.Column('Message', db.VARCHAR)
                                    )
        self.logs: list[Log] = []
        self.metadata.create_all(self.engine)
        self.AllPeerJobs = AllPeerJobs
    def log(self, JobID: str, Status: bool = True, Message: str = "") -> bool:
        try:
            with self.engine.begin() as conn:
                conn.execute(
                    self.jobLogTable.insert().values(
                        {
                            "LogID": str(uuid.uuid4()), 
                            "JobID": JobID, 
                            "Status": Status, 
                            "Message": Message
                        }
                    )
                )
        except Exception as e:
            print(f"[WGDashboard] Peer Job Log Error: {str(e)}")
            return False
        return True

    def getLogs(self, all: bool = False, configName = None) -> list[Log]:
        logs: list[Log] = []
        try:
            allJobs = self.AllPeerJobs.getAllJobs(configName)
            allJobsID = [x.JobID for x in allJobs]
            stmt = self.jobLogTable.select().where(self.jobLogTable.columns.JobID.in_(
                allJobsID
            ))
            table = self.loggerdb.execute(stmt).fetchall()            
            for l in table:
                logs.append(
                    Log(l.LogID, l.JobID, l.LogDate.strftime("%Y-%m-%d %H:%M:%S"), l.Status, l.Message))
        except Exception as e:
            print(e)
            return logs
        return logs