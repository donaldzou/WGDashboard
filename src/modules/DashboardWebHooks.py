import uuid
from datetime import datetime

from pydantic import BaseModel
import sqlalchemy as db
from .ConnectionString import ConnectionString

WebHookActions = ['peer_created', 'peer_deleted', 'peer_updated']
class WebHook(BaseModel):
    WebHookID: str = ''
    PayloadURL: str = ''
    ContentType: str = 'application/json'
    Headers: dict[str, dict[str, str]] = {}
    VerifySSL: bool = True
    SubscribedActions: list[str] = WebHookActions
    IsActive: bool = True
    CreationDate: datetime = ''
    Notes: str = ''

class DashboardWebHooks:
    def __init__(self, DashboardConfig):
        self.engine = db.create_engine(ConnectionString("wgdashboard"))
        self.metadata = db.MetaData()
        self.webHooksTable = db.Table(
            'DashboardWebHooks', self.metadata,
            db.Column('WebHookID', db.String(255), nullable=False, primary_key=True),
            db.Column('PayloadURL', db.Text, nullable=False),
            db.Column('ContentType', db.String(255), nullable=False),
            db.Column('Headers', db.JSON),
            db.Column('VerifySSL', db.Boolean, nullable=False),
            db.Column('SubscribedActions', db.JSON),
            db.Column('IsActive', db.Boolean, nullable=False),
            db.Column('CreationDate',
                      (db.DATETIME if DashboardConfig.GetConfig("Database", "type")[1] == 'sqlite' else db.TIMESTAMP),
                      server_default=db.func.now(),
                      nullable=False),
            db.Column('Notes', db.Text),
            extend_existing=True
        )
        self.metadata.create_all(self.engine)
        self.WebHooks: list[WebHook] = []
        self.__getWebHooks()
        
    def __getWebHooks(self):
        with self.engine.connect() as conn:
            webhooks = conn.execute(
                self.webHooksTable.select().order_by(
                    self.webHooksTable.c.CreationDate
                )
            ).mappings().fetchall()
            self.WebHooks.clear()
            self.WebHooks = [WebHook(**webhook) for webhook in webhooks]
            
    def GetWebHooks(self):
        self.__getWebHooks()
        return list(map(lambda x : x.model_dump(), self.WebHooks))
    
    def CreateWebHook(self) -> WebHook:
        return WebHook(WebHookID=str(uuid.uuid4()))
    
    def SearchWebHook(self, webHook: WebHook) -> WebHook | None:
        try:
            first = next(filter(lambda x : x.WebHookID == webHook.WebHookID, self.WebHooks))
        except StopIteration:
            return None
        return first
    
    def UpdateWebHook(self, webHook: dict[str, str]) -> tuple[bool, str] | tuple[bool, None]:
        try:
            webHook = WebHook(**webHook)
            
            if len(webHook.PayloadURL) == 0:
                return False, "Payload URL cannot be empty"
            
            if len(webHook.ContentType) == 0 or webHook.ContentType not in ['application/json', 'application/x-www-form-urlencoded']:
                return False, "Content Type is invalid"
            
            
            with self.engine.begin() as conn:
                if self.SearchWebHook(webHook):
                    conn.execute(
                        self.webHooksTable.update().values(
                            webHook.model_dump(exclude={'WebHookID'})
                        ).where(
                            self.webHooksTable.c.WebHookID == webHook.WebHookID
                        )
                    )
                else:
                    webHook.CreationDate = datetime.now()
                    conn.execute(
                        self.webHooksTable.insert().values(
                            webHook.model_dump()
                        )
                    )
            self.__getWebHooks()
        except Exception as e:
            return False, str(e)
        return True, None
    
    def DeleteWebHook(self, webHook) -> tuple[bool, str] | tuple[bool, None]:
        try:
            webHook = WebHook.model_validate(webHook)
            with self.engine.begin() as conn:
                conn.execute(
                    self.webHooksTable.delete().where(
                        self.webHooksTable.c.WebHookID == webHook.WebHookID
                    )
                )
        except Exception as e:
            return False, str(e)
        return True, None