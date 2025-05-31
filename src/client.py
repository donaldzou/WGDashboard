from flask import Blueprint, render_template, abort, request, Flask, current_app
import os
client = Blueprint('client', __name__, template_folder=os.path.abspath("./static/client/dist"))

def ResponseObject(status=True, message=None, data=None, status_code = 200) -> Flask.response_class:
    response = Flask.make_response(current_app, {
        "status": status,
        "message": message,
        "data": data
    })
    response.status_code = status_code
    response.content_type = "application/json"
    return response


prefix = '/client'


@client.before_request
def clientBeforeRequest():
    if request.method.lower() == 'options':
        return ResponseObject(True)

@client.get(prefix)
def clientIndex():
    return render_template('client.html')

