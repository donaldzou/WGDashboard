"""
Dashboard Logger Class
"""
import os, uuid
import sqlalchemy as db
from datetime import datetime

class DashboardLogger:
    def __init__(self, CONFIGURATION_PATH):
        self.engine = db.create_engine(f'sqlite:///{os.path.join(CONFIGURATION_PATH, "db", "wgdashboard_log.db")}')
        self.loggerdb = self.engine.connect()
        self.metadata = db.MetaData()
        self.dashboardLoggerTable = db.Table('DashboardLog', self.metadata,
                                             db.Column('LogID', db.VARCHAR, nullable=False, primary_key=True),
                                             db.Column('LogDate', db.DATETIME,
                                                       server_default=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                             db.Column('URL', db.VARCHAR),
                                             db.Column('IP', db.VARCHAR),
                                             
                                             db.Column('Status', db.VARCHAR, nullable=False),
                                             db.Column('Message', db.VARCHAR)
                                             )
        self.metadata.create_all(self.engine)
        self.log(Message="WGDashboard started")

    def log(self, URL: str = "", IP: str = "", Status: str = "true", Message: str = "") -> bool:
        try:
            with self.engine.begin() as conn:
                conn.execute(
                    self.dashboardLoggerTable.insert().values(
                        LogID=str(uuid.uuid4()),
                        URL=URL,
                        IP=IP,
                        Status=Status,
                        Message=Message
                    )
                )
            return True
        except Exception as e:
            print(f"[WGDashboard] Access Log Error: {str(e)}")
            return False