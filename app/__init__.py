from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)

LIVE_PLAY = 'live_play'
RECORDING = 'record'
JUKEBOX = 'jukebox'
play_mode = LIVE_PLAY

from app import routes
from app import midiloop

bootstrap = Bootstrap(app)
