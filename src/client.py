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
        if session.get("username") is None or session.get("role") != "client":
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
        return ResponseObject(status, msg)

    @client.get(prefix)
    @login_required
    def ClientIndex():
        print(wireguardConfigurations.keys())
        return render_template('client.html')
    
    return client