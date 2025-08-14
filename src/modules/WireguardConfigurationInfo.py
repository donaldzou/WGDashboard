from pydantic import BaseModel, PositiveInt

class OverridePeerSettingsClass(BaseModel):
    DNS: str = ''
    EndpointAllowedIPs: str = ''
    MTU: str | int = ''
    PersistentKeepalive: int | str = ''
    PeerRemoteEndpoint: str = ''
    ListenPort: int | str = ''
    
class PeerGroupsClass(BaseModel):
    Description: str = ''
    BackgroundColor: str = ''
    Peers: list[str] = []

class WireguardConfigurationInfo(BaseModel):
    Description: str = ''
    OverridePeerSettings: OverridePeerSettingsClass = OverridePeerSettingsClass(**{})
    PeerGroups: dict[str, PeerGroupsClass] = {}


if __name__ == '__main__':
    d = WireguardConfigurationInfo.model_validate_json("{\"Description\": \"Hi!\"}")
    print(d.model_dump())