from .PeerShareLink import PeerShareLink
import sqlalchemy as db
from datetime import datetime
import uuid

"""
Peer Share Links
"""
class PeerShareLinks:
    def __init__(self, DashboardConfig):
        self.Links: list[PeerShareLink] = []
        self.engine = db.create_engine(DashboardConfig.getConnectionString("wgdashboard"))
        self.metadata = db.MetaData()
        self.peerShareLinksTable = db.Table(
            'PeerShareLinks', self.metadata,
            db.Column('ShareID', db.String(255), nullable=False, primary_key=True),
            db.Column('Configuration', db.String(255), nullable=False),
            db.Column('Peer', db.String(255), nullable=False),
            db.Column('ExpireDate', (db.DATETIME if DashboardConfig.GetConfig("Database", "type")[1] == 'sqlite' else db.TIMESTAMP)),
            db.Column('SharedDate', (db.DATETIME if DashboardConfig.GetConfig("Database", "type")[1] == 'sqlite' else db.TIMESTAMP),
                      server_default=db.func.now()),
        )
        self.metadata.create_all(self.engine)
        self.__getSharedLinks()
    def __getSharedLinks(self):
        self.Links.clear()
        with self.engine.connect() as conn:
            allLinks = conn.execute(
                self.peerShareLinksTable.select().where(
                    db.or_(self.peerShareLinksTable.columns.ExpireDate == None, self.peerShareLinksTable.columns.ExpireDate > datetime.now())
                )
            ).mappings().fetchall()
            for link in allLinks:
                self.Links.append(PeerShareLink(**link))



    def getLink(self, Configuration: str, Peer: str) -> list[PeerShareLink]:
        self.__getSharedLinks()
        return list(filter(lambda x : x.Configuration == Configuration and x.Peer == Peer, self.Links))

    def getLinkByID(self, ShareID: str) -> list[PeerShareLink]:
        self.__getSharedLinks()
        return list(filter(lambda x : x.ShareID == ShareID, self.Links))

    def addLink(self, Configuration: str, Peer: str, ExpireDate: datetime = None) -> tuple[bool, str]:
        try:
            newShareID = str(uuid.uuid4())
            with self.engine.begin() as conn:
                if len(self.getLink(Configuration, Peer)) > 0:
                    conn.execute(
                        self.peerShareLinksTable.update().values(
                            {
                                "ExpireDate": datetime.now()
                            }
                        ).where(db.and_(self.peerShareLinksTable.columns.Configuration == Configuration, self.peerShareLinksTable.columns.Peer == Peer))
                    )

                conn.execute(
                    self.peerShareLinksTable.insert().values(
                        {
                            "ShareID": newShareID,
                            "Configuration": Configuration,
                            "Peer": Peer,
                            "ExpireDate": ExpireDate
                        }
                    )
                )
            self.__getSharedLinks()
        except Exception as e:
            return False, str(e)
        return True, newShareID

    def updateLinkExpireDate(self, ShareID, ExpireDate: datetime = None) -> tuple[bool, str]:
        with self.engine.begin() as conn:
            conn.execute(
                self.peerShareLinksTable.update().values(
                    {
                        "ExpireDate": ExpireDate
                    }
                ).where(db.and_(self.peerShareLinksTable.columns.ShareID == ShareID))
            )
        self.__getSharedLinks()
        return True, ""