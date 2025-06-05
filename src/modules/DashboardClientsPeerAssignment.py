from .ConnectionString import ConnectionString
from .DashboardLogger import DashboardLogger
import sqlalchemy as db


class DashboardClientsPeerAssignment:
    def __init__(self):
        self.logger = DashboardLogger()
        self.engine = db.create_engine(ConnectionString("wgdashboard"))
        self.metadata = db.MetaData()
        
        self.dashboardClientsPeerAssignmentTable = db.Table(
            'DashboardClientsPeerAssignment', self.metadata,
            db.Column('AssignmentID', db.String(255), nullable=False, primary_key=True),
            db.Column('ClientID', db.String(255), nullable=False, index=True),
            db.Column('ConfigurationName', db.String(255)),
            db.Column('PeerID', db.String(500)),
            db.Column('AssignedDate',
                      (db.DATETIME if 'sqlite:///' in ConnectionString("wgdashboard") else db.TIMESTAMP),
                      server_default=db.func.now()),
            db.Column('UnassignedDate',
                      (db.DATETIME if 'sqlite:///' in ConnectionString("wgdashboard") else db.TIMESTAMP)),
            extend_existing=True
        )
        self.metadata.create_all(self.engine)
        self.assignments = []
    
    def __getAssignments(self):
        with self.engine.connect() as conn:
            self.assignments = conn.execute(
                self.dashboardClientsPeerAssignmentTable.select().where(
                    self.dashboardClientsPeerAssignmentTable.c.UnassignedDate is None
                )
            ).mappings().fetchall()
            
    def AssignClient(self, ClientID, ConfigurationName, PeerID):
        pass
    
    def UnassignClient(self, AssignmentID):
        pass
    
    def GetAssignedClient(self, ConfigurationName, PeerID):
        pass
    
    def GetAssignedPeers(self, ClientID):
        pass