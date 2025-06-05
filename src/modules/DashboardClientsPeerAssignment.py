import uuid

from .ConnectionString import ConnectionString
from .DashboardLogger import DashboardLogger
import sqlalchemy as db

from .WireguardConfiguration import WireguardConfiguration


class DashboardClientsPeerAssignment:
    def __init__(self, wireguardConfigurations: dict[str, WireguardConfiguration]):
        self.logger = DashboardLogger()
        self.engine = db.create_engine(ConnectionString("wgdashboard"))
        self.metadata = db.MetaData()
        self.wireguardConfigurations = wireguardConfigurations
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
        self.__getAssignments()
    
        self.AssignClient("0117a895-bd8b-4ba2-9116-6658372417fb", "wg0", "3kv6Bo46u7ULT07B3I1VHw/rYomVnrCD5TFU369jRSc=")
        self.GetAssignedPeers("0117a895-bd8b-4ba2-9116-6658372417fb")
        
    def __getAssignments(self):
        with self.engine.connect() as conn:
            self.assignments = conn.execute(
                self.dashboardClientsPeerAssignmentTable.select().where(
                    self.dashboardClientsPeerAssignmentTable.c.UnassignedDate == db.null()
                )
            ).mappings().fetchall()
            
    def AssignClient(self, ClientID, ConfigurationName, PeerID):
        existing = list(
            filter(lambda e: 
                   e['ClientID'] == ClientID and 
                   e['ConfigurationName'] == ConfigurationName and
                   e['PeerID'] == PeerID, self.assignments)
        )
        if len(existing) == 0:
            if ConfigurationName in self.wireguardConfigurations.keys():
                config = self.wireguardConfigurations.get(ConfigurationName)
                peer = list(filter(lambda x : x.id == PeerID, config.Peers))
                if len(peer) == 1:
                    with self.engine.begin() as conn:
                        data = {
                            "AssignmentID": uuid.uuid4(),
                            "ClientID": ClientID,
                            "ConfigurationName": ConfigurationName,
                            "PeerID": PeerID
                        }
                        conn.execute(
                            self.dashboardClientsPeerAssignmentTable.insert().values(data)
                        )
                    return True, data
        return False, None
    
    def UnassignClient(self, AssignmentID):
        pass
    
    def GetAssignedClient(self, ConfigurationName, PeerID):
        pass
    
    def GetAssignedPeers(self, ClientID):
        peers = []
        assigned = list(
            filter(lambda e:
                   e['ClientID'] == ClientID, self.assignments)
        )
        
        for a in assigned:
            peer = filter(lambda e : e.id == a['PeerID'], 
                          self.wireguardConfigurations[a['ConfigurationName']].Peers)
            for p in peer:
                peers.append({
                    'id': p.id,
                    'private_key': p.private_key,
                    'name': p.name,
                    'received_data': p.total_receive + p.cumu_receive,
                    'sent_data': p.total_sent + p.cumu_sent,
                    'data': p.total_data + p.cumu_data,
                    'status': p.status,
                    'latest_handshake': p.latest_handshake,
                    'allowed_ip': p.allowed_ip,
                    'jobs': p.jobs,
                    'configuration_name': a['ConfigurationName'],
                    'peer_configuration_data': p.downloadPeer()
                })
        
        print(peers)
        return peers