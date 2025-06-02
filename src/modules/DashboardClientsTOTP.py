import datetime
import hashlib
import uuid

import sqlalchemy as db
from .ConnectionString import ConnectionString


class DashboardClientsTOTP:
    def __init__(self):
        self.engine = db.create_engine(ConnectionString("wgdashboard"))
        self.metadata = db.MetaData()
        self.dashboardClientsTOTPTable = db.Table(
            'DashboardClientsTOTPTokens', self.metadata,
            db.Column("Token", db.String(500), primary_key=True, index=True),
                db.Column("ClientID", db.String(500), index=True),
                db.Column(
                    "ExpireTime", (db.DATETIME if 'sqlite:///' in ConnectionString("wgdashboard") else db.TIMESTAMP)
                )
        )
        self.metadata.create_all(self.engine)
        
    def GenerateToken(self, ClientID) -> str:
        token = hashlib.sha512(f"{ClientID}_{datetime.datetime.now()}_{uuid.uuid4()}".encode()).hexdigest()
        with self.engine.begin() as conn:
            conn.execute(
                self.dashboardClientsTOTPTable.update().values({
                    "ExpireTime": datetime.datetime.now()
                }).where(
                   db.and_(self.dashboardClientsTOTPTable.c.ClientID == ClientID,  self.dashboardClientsTOTPTable.c.ExpireTime > datetime.datetime.now())
                )
            )
            
            
            conn.execute(
                self.dashboardClientsTOTPTable.insert().values({
                    "Token": token,
                    "ClientID": ClientID,
                    "ExpireTime": datetime.datetime.now() + datetime.timedelta(minutes=10)
                })
            )
        
        return token
        