from flask import render_template, jsonify, request
from app import app
from midiserver.command import command
from config import *
from safety import *
import glob
import os
import string
import subprocess

def get_songs():
    songs = []
    for f in glob.glob(os.path.join(JUKEBOX_DIR, '*.mid')):
        try:
            song_stat = os.stat(f)
        except OSError:
            continue
        songs.append({'name': os.path.basename(f), 'mtime': os.stat(f).st_mtime})
    return songs

@app.route('/songs', methods=['POST'])
def songs():
    return jsonify({'songs': get_songs()})

@app.route('/')
@app.route('/index')
def index():
    songs = get_songs()
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

@app.route('/reset', methods=['POST'])
def reset():
    success, result = command(RESET)
    return jsonify({'status': success})

@app.route('/panic', methods=['POST'])
def panic():
    cmd = ['/usr/bin/sudo', '/bin/systemctl', 'restart', 'midiserver.service']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    out,err = p.communicate()
    return jsonify({'stdout': out, 'stderr': err})

@app.route('/lightsout', methods=['POST'])
def lightsout():
    cmd = ['/usr/bin/sudo', '/sbin/shutdown', '-r', 'now']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    out,err = p.communicate()
    return jsonify({'stdout': out, 'stderr': err})

@app.route('/mode', methods=['GET'])
def current_mode():
    success, result = command(MODE)
    if not success:
        return jsonify({'status': False})
    return jsonify({'status': True, 'mode': result[1]})

@app.route('/rename', methods=['POST'])
def rename():
    # Really should just handle sanitization in one place
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
    return jsonify({'status': True, 'filename': new_name})

@app.route('/single_play', methods=['POST'])
def single_play():
    song_name = slugify(request.form['song_name'])
    if song_name is None or song_name == '':
        return jsonify({'reason': 'Recording name invalid!'}), 500
    if not song_name.endswith('.mid'):
        song_name = song_name + '.mid'
    success, result = command(SINGLE_PLAY, song_name)
    return jsonify({'status': success, 'result': result})
