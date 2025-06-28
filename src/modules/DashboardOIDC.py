import os
import json
import requests
from jose import jwt


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
    
    def VerifyToken(self, provider, code, redirect_uri):
        if not all([provider, code, redirect_uri]):
            return False, ""
        
        if provider not in self.providers.keys():
            return False, "Provider does not exist"
        
        provider = self.providers.get(provider)
        oidc_config = requests.get(f"{provider.get('issuer')}.well-known/openid-configuration").json()

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": provider.get('client_id'),
            "client_secret": provider.get('client_secret')
        }

        tokens = requests.post(oidc_config.get('token_endpoint'), data=data).json()


        id_token = tokens.get('id_token')





        jwks_uri = oidc_config.get("jwks_uri")
        issuer = oidc_config.get("issuer")
        jwks = requests.get(jwks_uri).json()

        from jose.utils import base64url_decode
        from jose.backends.cryptography_backend import CryptographyRSAKey
        
        # Choose the right key based on `kid` in token header
        headers = jwt.get_unverified_header(id_token)
        kid = headers["kid"]
        
        # Find the key with the correct `kid`
        key = next(k for k in jwks["keys"] if k["kid"] == kid)
        
        # Use the key to verify token
        payload = jwt.decode(
            id_token,
            key,
            algorithms=[key["alg"]],
            audience=provider.get('client_id'),
            issuer=issuer
        )
        
        print(payload)  # This contains the user's claims
        
    
    def ReadFile(self):
        decoder = json.JSONDecoder()
        self.providers = decoder.decode(
            open(DashboardOIDC.ConfigurationFilePath, 'r').read()
        )