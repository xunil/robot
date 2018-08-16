from flask import render_template, jsonify, request
from app import app
from midiserver.command import command
from config import *
import glob
import os
import string

VALID_CHARS = frozenset("-_.() %s%s" % (string.ascii_letters, string.digits))

def slugify(s):
    return ''.join(c for c in s if c in VALID_CHARS)

@app.route('/')
@app.route('/index')
def index():
    songs = [os.path.basename(f) for f in glob.glob(os.path.join(JUKEBOX_DIR, '*.mid'))]
    return render_template('index.html', title='Home', songs=songs)

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

@app.route('/rename', methods=['POST'])
def rename():
    old_name = slugify(request.form['old'])
    new_name = slugify(request.form['new'])
    if old_name is None or old_name == '' or new_name is None or new_name == '':
        return jsonify({'reason': 'Recording name invalid!'}), 500
    if not new_name.endswith('.mid'):
        new_name = new_name + '.mid'
    try:
        os.rename(os.path.join(RECORDING_DIR, old_name), os.path.join(JUKEBOX_DIR, new_name))
    except OSError as e:
        return jsonify({'reason': str(e)}), 500
    return jsonify({'filename': new_name})
