#!/usr/bin/env
import cPickle as pickle
import logging
import midi
from midi import sequencer_alsa as sequencer
import socket
import sys
from threading import Thread
import time

CLIENT = 24
PORT   = 0
SKY_PI_ADDR = '192.168.2.48'
SKY_PI_PORT = 23840
CMD_PORT = 23850

LIVE_PLAY = 'live_play'
JUKEBOX = 'jukebox'
RECORD = 'record'

RECORDING_DIR = '/home/pi/recordings'

class MIDIServer:
    def __init__(self):
        logging.basicConfig(filename='midiserver.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
        self.mode = LIVE_PLAY

    def setup_midi_sequencer(self):
        # TODO: May need to adjust sequencer resolution
        self.seq = sequencer.SequencerRead(sequencer_resolution=128)
        # TODO: Sequencer device discovery
        self.seq.subscribe_port(CLIENT, PORT)
        self.seq.start_sequencer()

    def handle_command_channel(self):
        self.cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cmd.bind(('0.0.0.0', CMD_PORT))
        self.cmd.listen(1)
        try:
            while True:
                conn,cli_addr = self.cmd.accept()
                logging.info('Command channel connection from %s', cli_addr)
                while True:
                    data = conn.recv(4096)
                    command = data.strip()
                    if command == 'mode':
                        conn.sendall('%s\n' % self.mode)
                    elif command == 'record':
                        self.output_file,self.output_filename = mkstemp(suffix='.mid', prefix='recording', dir=RECORDING_DIR)
                        self.mode = RECORD
                        conn.sendall('OK\n')
                    elif command == 'live_play':
                        self.mode = LIVE_PLAY
                        conn.sendall('OK\n')
                    else:
                        conn.sendall('ERR\n')
                            
        finally:
            conn.close()
            

    def connect_to_sky_pi(self):
        while True:
            try:
                self.skypi = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((SKY_PI_ADDR, SKY_PI_PORT))
                break
            except socket.error as e:
                logging.info('Failed to connect to Sky Pi: %s' % e)
                logging.info('Sleeping 3 seconds and trying again.')
                time.sleep(3)

    def handle_midi_loop(self):
        while True:
            self.connect_to_sky_pi()
            while True:
                try:
                    event = seq.event_read()
                    logging.debug(repr(event))
                    self.skypi.sendall(pickle.dumps(event, pickle.HIGHEST_PROTOCOL))
                except socket.error:
                    break
                finally:
                    self.skypi.close()
            logging.warn('Lost connection to Sky Pi, reconnecting...')

    def run(self):
        self.command_thread = Thread(target=self.handle_command_channel, args=())
        self.command_thread.start()
        self.setup_midi_sequencer()
        self.midi_thread = Thread(target=self.handle_midi_loop, args=())
        self.midi_thread.start()



if __name__ == '__main__':
    s = MIDIServer()
    s.run()
