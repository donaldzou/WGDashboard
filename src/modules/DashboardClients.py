import sqlalchemy as db
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.testing.schema import mapped_column

from .ConnectionString import ConnectionString


class DashboardClients:
    def __init__(self):
        self.engine = db.create_engine(ConnectionString("wgdashboard"))
        self.metadata = db.MetaData()
        
        self.dashboardClientsTable = db.Table(
            'DashboardClients', self.metadata,
            db.Column('ClientID', db.String(255), nullable=False, primary_key=True),
            db.Column('Email', db.String(255), nullable=False, index=True),
            db.Column('Password', db.String(500)),
            db.Column('TotpKey', db.String(500)),
            db.Column('TotpKeyVerified', db.Integer),
            db.Column('CreatedDate', 
                      (db.DATETIME if 'sqlite:///' in ConnectionString("wgdashboard") else db.TIMESTAMP),
                      server_default=db.func.now()),
            db.Column('DeletedDate', 
                      (db.DATETIME if 'sqlite:///' in ConnectionString("wgdashboard") else db.TIMESTAMP)),
            extend_existing=True,
        )

        self.dashboardClientsInfoTable = db.Table(
            'DashboardClientsInfo', self.metadata,
            db.Column('ClientID', db.String(255), nullable=False, primary_key=True),
            db.Column('Firstname', db.String(500)),
            db.Column('Lastname', db.String(500)),
            extend_existing=True,
        )

        self.metadata.create_all(self.engine)
        self.Clients = []
        self.__getClients()
        print('hi')
        print(self.Clients)
        
    def __getClients(self):
        with self.engine.connect() as conn:
            self.Clients = conn.execute(
                db.select(
                    self.dashboardClientsTable.c.ClientID,
                    self.dashboardClientsTable.c.Email,
                    self.dashboardClientsTable.c.CreatedDate
                ).where(
                    self.dashboardClientsTable.c.DeletedDate is None)
                ).mappings().fetchall()
            
    
    
    def SignUp(self, Email, Password, ConfirmPassword) -> tuple[bool, str]:
        pass
    
        