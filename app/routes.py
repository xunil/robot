from flask import render_template, jsonify
from app import app
from midiserver.command import command
from config import *

play_mode = None

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/live_play', methods=['POST'])
def live_play():
    success, result = command(LIVE_PLAY)
    return jsonify({'status': success})

@app.route('/start_record', methods=['POST'])
def start_record():
    success, result = command(RECORD)
    if not success:
        return jsonify({'status': False})
    return jsonify({'status': True, 'filename': result[1]})

@app.route('/stop_record', methods=['POST'])
def stop_record():
    success, result = command(LIVE_PLAY)
    if not success:
        return jsonify({'status': False})
    return jsonify({'status': True, 'filename': result[1]})

@app.route('/jukebox', methods=['POST'])
def jukebox():
    success, result = command(JUKEBOX)
    return jsonify({'status': success})

@app.route('/mode', methods=['GET'])
def current_mode():
    success, result = command(MODE)
    if not success:
        return jsonify({'status': False})
    return jsonify({'status': True, 'mode': result[1]})

