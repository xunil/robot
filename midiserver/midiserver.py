#!/usr/bin/env
import cPickle as pickle
import logging
import mido
from mido import Message, MidiFile, MidiTrack
from os.path import dirname, abspath
import socket
import sys
from tempfile import mkstemp
from threading import Thread
import time
import re

sys.path.append(dirname(dirname(abspath(__file__))))
from config import *

current_milli_time = lambda: int(round(time.time() * 1000))

class MIDIServer:
    def __init__(self):
        logging.basicConfig(filename='midiserver.log', format='%(asctime)s [%(threadName)s] %(message)s', level=logging.DEBUG)
        self.mode = LIVE_PLAY

    def find_midi_client(self):
        client_name = CLIENT_NAME
        client_found = False
        for port_name in mido.get_output_names():
            if port_name.split(':')[0] == client_name:
                client_name = port_name
                client_found = True
                break

        if not client_found:
            return None
        return client_name

    def get_midi_sequencer(self):
        client_name = self.find_midi_client()
        if client_name is None:
            print >>sys.stderr, 'Could not find MIDI client named %s' % CLIENT_NAME
            sys.exit(1)
        return mido.open_input(client_name)

    def handle_command_channel(self):
        try:
            self.cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cmd.bind(('0.0.0.0', CMD_PORT))
            self.cmd.listen(1)
            while True:
                conn,cli_addr = self.cmd.accept()
                logging.info('Command channel connection from %s', cli_addr)
                while True:
                    data = conn.recv(4096)
                    if data:
                        reply = 'ERR\n'
                        command = data.strip()
                        logging.debug('Command received: %s' % command)
                        if command == 'mode':
                            reply = 'OK:%s\n' % self.mode
                        elif command == 'record':
                            self.output_file,self.output_filename = mkstemp(suffix='.mid', prefix='recording', dir=RECORDING_DIR)
                            self.mode = RECORD
                            self.recording_thread = Thread(target=self.handle_recording, name='Recording', args=())
                            self.recording_thread.start()
                            reply = 'OK:%s\n' % self.output_filename
                        elif command == 'live_play':
                            self.mode = LIVE_PLAY
                            reply = 'OK:%s\n' % self.output_filename
                        else:
                            logging.debug('Unknown command %s' % command)
                        logging.debug('Sending reply: %s' % reply.strip())
                        conn.sendall(reply)
                    else:
                        logging.debug('Closing command channel connection from %s', cli_addr)
                        conn.close()
                        break
        finally:
            if conn:
                conn.close()

    def connect_to_sky_pi(self):
        while True:
            try:
                self.skypi = sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((SKY_PI_ADDR, SKY_PI_PORT))
                logging.info('Connected to Sky Pi')
                break
            except socket.error as e:
                logging.info('Failed to connect to Sky Pi: %s' % e)
                logging.info('Sleeping 3 seconds and trying again.')
                time.sleep(3)

    def handle_midi_loop(self):
        self.midi_input = self.get_midi_sequencer()
        while True:
            self.connect_to_sky_pi()
            try:
                while True:
                    event = self.midi_input.receive()
                    logging.debug(repr(event))
                    self.skypi.sendall(pickle.dumps(event, pickle.HIGHEST_PROTOCOL))
            except socket.error:
                break
            finally:
                self.skypi.close()
            logging.warn('Lost connection to Sky Pi, reconnecting...')

    def handle_recording(self):
        logging.info('Starting recording thread')
        logging.info('Getting a handle to the sequencer...')
        self.midi_recording = self.get_midi_sequencer()
        logging.info('Got sequencer.')
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        logging.info('About to enter loop, output file: %s' % repr(self.output_file))
        last_event_time = None
        while True:
            for event in self.midi_recording.iter_pending():
                now_time = current_milli_time()
                if last_event_time is not None:
                    event.time = now_time - last_event_time
                    # Otherwise event.time stays at 0.
                last_event_time = now_time
                track.append(event)
                logging.info('Appending event to track: %s' % event)
            if self.mode != RECORD:
                break
            time.sleep(0.001)
        logging.info('Saving to output_file %s (filename %s)' % (repr(self.output_file), self.output_filename))
        mid.save(self.output_file)
        self.midi_recording.close()
        logging.info('Exiting recording thread')

    def run(self):
        self.command_thread = Thread(target=self.handle_command_channel, name='Command', args=())
        self.command_thread.start()
        self.midi_thread = Thread(target=self.handle_midi_loop, name='MIDI', args=())
        self.midi_thread.start()
        self.midi_thread.join()
        self.command_thread.join()


if __name__ == '__main__':
    s = MIDIServer()
    s.run()
