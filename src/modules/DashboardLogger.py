"""
Dashboard Logger Class
"""
import uuid
import sqlalchemy as db


class DashboardLogger:
    def __init__(self, DashboardConfig):
        self.engine = db.create_engine(DashboardConfig.getConnectionString("wgdashboard_log"))
        self.metadata = db.MetaData()
        self.dashboardLoggerTable = db.Table('DashboardLog', self.metadata,
                                             db.Column('LogID', db.VARCHAR, nullable=False, primary_key=True),
                                             db.Column('LogDate', (db.DATETIME if DashboardConfig.GetConfig("Database", "type")[1] == 'sqlite' else db.TIMESTAMP),
                                                       server_default=db.func.now()),
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