from flask import render_template, jsonify
from app import app
from midiserver_command import midiserver_command

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/live_play', methods=['POST'])
def live_play():
    # XXX: connect to command socket and send command
    play_mode = LIVE_PLAY
    return jsonify({'status': 'OK'})

@app.route('/start_record', methods=['POST'])
def start_record():
    play_mode = RECORD
    return jsonify({'status': 'OK'})

@app.route('/stop_record', methods=['POST'])
def stop_record():
    play_mode = LIVE_PLAY
    return jsonify({'status': 'OK'})

@app.route('/jukebox', methods=['POST'])
def jukebox():
    play_mode = JUKEBOX
    return jsonify({'status': 'OK'})

@app.route('/mode', methods=['GET'])
def current_mode():
    return jsonify({'mode': play_mode})

