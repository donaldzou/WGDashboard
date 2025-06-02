from functools import wraps

from flask import Blueprint, render_template, abort, request, Flask, current_app, session
import os

from modules.WireguardConfiguration import WireguardConfiguration
from modules.DashboardConfig import DashboardConfig

def ResponseObject(status=True, message=None, data=None, status_code = 200) -> Flask.response_class:
    response = Flask.make_response(current_app, {
        "status": status,
        "message": message,
        "data": data
    })
    response.status_code = status_code
    response.content_type = "application/json"
    return response

def login_required(f):
    @wraps(f)
    def func(*args, **kwargs):
        if session.get("username") is None or session.get("totpVerified") is None or not session.get("totpVerified") or session.get("role") != "client":
            return ResponseObject(False, "Unauthorized access.", data=None, status_code=401)
        return f(*args, **kwargs)
    return func

def createClientBlueprint(wireguardConfigurations: dict[WireguardConfiguration], dashboardConfig: DashboardConfig):
    from modules.DashboardClients import DashboardClients
    DashboardClients = DashboardClients()
    client = Blueprint('client', __name__, template_folder=os.path.abspath("./static/client/dist"))
    prefix = f'{dashboardConfig.GetConfig("Server", "app_prefix")[1]}/client'
    
    
    @client.before_request
    def clientBeforeRequest():
        if request.method.lower() == 'options':
            return ResponseObject(True)
        
    
    @client.post(f'{prefix}/api/signup')
    def ClientAPI_SignUp():
        data = request.json
        status, msg = DashboardClients.SignUp(**data)
        return ResponseObject(status, msg)
    
    @client.post(f'{prefix}/api/signin')
    def ClientAPI_SignIn():
        data = request.json
        status, msg = DashboardClients.SignIn(**data)
        if status:
            session['username'] = data.get('Email')
            session['role'] = 'client'
            session['totpVerified'] = False
        return ResponseObject(status, msg)
    
    @client.get(f'{prefix}/api/signin/totp')
    def ClientAPI_SignIn_TOTP():
        token = request.args.get('Token', None)
        if not token:
            return ResponseObject(False, "Please provide TOTP token")
        
        status, msg = DashboardClients.SignIn_GetTotp(token)
        return ResponseObject(status, msg)

    @client.post(f'{prefix}/api/signin/totp')
    def ClientAPI_SignIn_ValidateTOTP():
        data = request.json
        token = data.get('Token', None)
        userProvidedTotp = data.get('UserProvidedTOTP', None)
        if not all([token, userProvidedTotp]):
            return ResponseObject(False, "Please fill in all fields")
        status, msg = DashboardClients.SignIn_GetTotp(token, userProvidedTotp)
        if status:
            if session.get('username') is None:
                return ResponseObject(False, "Sign in status is invalid", status_code=401)
            session['totpVerified'] = True
        
        return ResponseObject(status, msg)
    
    @client.get(prefix)
    def ClientIndex():
        return render_template('client.html')
    
    @client.get(f'{prefix}/api/validateAuthentication')
    @login_required
    def ClientAPI_ValidateAuthentication():
        return ResponseObject(True)
    
    @client.get(f'{prefix}/api/configurations')
    @login_required
    def ClientAPI_Configurations():
        return ResponseObject(True, "Ping Pong!")
    
    return client