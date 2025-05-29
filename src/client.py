from flask import Blueprint, render_template, abort
import os

client = Blueprint('client', __name__, template_folder=os.path.abspath("./static/client/dist"))


@client.get(f'/client')
def clientIndex():
    return render_template('client.html')
