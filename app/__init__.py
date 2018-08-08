from flask import Flask

app = Flask(__name__)

from app import routes
#from app.midiloop import activate_midiloop
from app import midiloop
