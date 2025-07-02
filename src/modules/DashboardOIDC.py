import os
import json
import requests
from jose import jwt
import certifi
from flask import current_app


class DashboardOIDC:
    ConfigurationPath = os.getenv('CONFIGURATION_PATH', '.')
    ConfigurationFilePath = os.path.join(ConfigurationPath, 'wg-dashboard-oidc-providers.json')
    def __init__(self):
        self.providers: dict[str, dict] = None
        self.__default = {
            'Provider': {
                'client_id': '',
                'client_secret': '',
                'issuer': '',
            },
        }
        
        if not os.path.exists(DashboardOIDC.ConfigurationFilePath):
            with open(DashboardOIDC.ConfigurationFilePath, "w+") as f:
                encoder = json.JSONEncoder(indent=4)
                f.write(encoder.encode(self.__default))
        
        self.ReadFile()
        
    def GetProviders(self):
        providers = {}
        for k in self.providers.keys():
            if all([self.providers[k]['client_id'], self.providers[k]['client_secret'], self.providers[k]['issuer']]):
                try:
                    oidc_config = requests.get(
                        f"{self.providers[k]['issuer'].strip('/')}/.well-known/openid-configuration",
                        verify=certifi.where()
                    ).json()
                    providers[k] = {
                        'client_id': self.providers[k]['client_id'],
                        'issuer': self.providers[k]['issuer'].strip('/')
                    }
                except Exception as e:
                    current_app.logger.error("Failed to request OIDC config for this provider: " + self.providers[k]['issuer'].strip('/'), exc_info=e)
        
        return providers
    
    def VerifyToken(self, provider, code, redirect_uri):
        try:
            if not all([provider, code, redirect_uri]):
                return False, ""

            if provider not in self.providers.keys():
                return False, "Provider does not exist"
    
            provider = self.providers.get(provider)
            oidc_config = requests.get(
                f"{provider.get('issuer').strip('/')}/.well-known/openid-configuration",
                verify=certifi.where()
    
            ).json()
    
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": provider.get('client_id'),
                "client_secret": provider.get('client_secret')
            }
    
            try:
                tokens = requests.post(oidc_config.get('token_endpoint'), data=data).json()
                if not all([tokens.get('access_token'), tokens.get('id_token')]):
                    return False, tokens.get('error_description', None)
            except Exception as e:
                return False, str(e)
            
            access_token = tokens.get('access_token')
            id_token = tokens.get('id_token')
            jwks_uri = oidc_config.get("jwks_uri")
            issuer = oidc_config.get("issuer")
            jwks = requests.get(jwks_uri, verify=certifi.where()).json()
    
            headers = jwt.get_unverified_header(id_token)
            kid = headers["kid"]
    
            key = next(k for k in jwks["keys"] if k["kid"] == kid)
            
            print(key)
            
            payload = jwt.decode(
                id_token,
                key,
                algorithms=[key["alg"]],
                audience=provider.get('client_id'),
                issuer=issuer,
                access_token=access_token
            )
    
            return True, payload
        except Exception as e:
            with current_app.app_context():
                current_app.logger.error('Read OIDC file failed. Reason: ' + str(e), provider, code, redirect_uri)
            return False, str(e)
        
    
    def ReadFile(self):
        decoder = json.JSONDecoder()
        try:
            self.providers = decoder.decode(
                open(DashboardOIDC.ConfigurationFilePath, 'r').read()
            )
        except Exception as e:
            with current_app.app_context():
                current_app.logger.error('Read OIDC file failed. Reason: ' + str(e))
            return False