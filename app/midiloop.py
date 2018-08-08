from app import app
import cPickle as pickle
import midi
from midi import sequencer
import socket
import sys
import threading

CLIENT = 20
PORT   = 0
SKY_PI_ADDR = '192.168.2.49'
SKY_PI_PORT = 23840


# TODO: Error handling, automatic restart
def midiloop(app):
    with app.app_context():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SKY_PI_ADDR, SKY_PI_PORT))

            # TODO: May need to adjust sequencer resolution
            seq = sequencer.SequencerRead(sequencer_resolution=128)
            # TODO: Sequencer device discovery
            seq.subscribe_port(CLIENT, PORT)
            seq.start_sequencer()

            while True:
                event = seq.event_read()
                evtyp = event.name
                tick = event.tick
                velocity = 0
                pitch = 0
                if isinstance(event, midi.NoteOnEvent):
                    velocity = event.velocity
                    pitch = event.pitch
                app.logger.debug(evtyp, 'tick:%s' % tick, 'velocity: %s' % velocity, 'pitch: %s' % pitch)
                sock.sendall(pickle.dumps(event, pickle.HIGHEST_PROTOCOL))
        finally:
            sock.close()

@app.before_first_request
def activate_midiloop():
    app.logger.info('Starting MIDI loop')
    thread = threading.Thread(target=midiloop, args=(app,))
    thread.start()
