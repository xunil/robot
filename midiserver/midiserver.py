#!/usr/bin/env
import glob
import logging
import mido
from mido import Message, MidiFile, MidiTrack
import os
from os.path import abspath, basename, dirname
import random
import select
import signal
import socket
import sys
from tempfile import mkstemp
from threading import Thread
import time

sys.path.append(dirname(dirname(abspath(__file__))))
from config import *
from safety import slugify

current_milli_time = lambda: int(round(time.time() * 1000))

class MIDIServer:
    def __init__(self):
        logging.basicConfig(filename='midiserver.log', format='%(asctime)s [%(threadName)s] %(message)s', level=logging.DEBUG)
        self.mode = LIVE_PLAY

    def find_midi_client(self):
        client_name = None
        client_found = False
        for port_name in mido.get_output_names():
            if port_name.split(':')[0] in MIDI_CLIENT_NAMES:
                client_name = port_name
                client_found = True
                break

        if not client_found:
            return None
        return client_name

    def get_midi_sequencer(self):
        client_name = self.find_midi_client()
        if client_name is None:
            print >>sys.stderr, 'Could not find MIDI client matching %s' % repr(MIDI_CLIENT_NAMES)
            sys.exit(1)
        return mido.open_input(client_name)

    def handle_command_channel(self):
        inputs = []
        self.output_filename = None
        try:
            self.cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cmd.bind(('0.0.0.0', CMD_PORT))
            self.cmd.listen(1)
            inputs.append(self.cmd)
            while True:
                readable, _, exceptional = select.select(inputs, [], inputs, 1.0)
                for s in readable:
                    if s is self.cmd:
                        conn,cli_addr = self.cmd.accept()
                        logging.info('Command channel connection from %s', cli_addr)
                        conn.setblocking(0)
                        inputs.append(conn)
                    else:
                        data = s.recv(4096)
                        if data:
                            reply = 'ERR\n'
                            data = data.strip()
                            command = data.split(':')[0]
                            args = data.split(':')[1:]
                            logging.debug('Command received: %s' % command)
                            if command == MODE:
                                reply = 'OK:%s\n' % self.mode
                            elif command == RECORD:
                                self.output_file,self.output_filename = mkstemp(suffix='.mid', prefix='recording', dir=RECORDING_DIR)
                                self.mode = RECORD
                                self.recording_thread = Thread(target=self.handle_recording, name='Recording', args=())
                                self.recording_thread.start()
                                reply = 'OK:%s\n' % basename(self.output_filename)
                            elif command == LIVE_PLAY:
                                self.mode = LIVE_PLAY
                                self.live_play_thread = Thread(target=self.handle_live_play, name='Live Play', args=())
                                self.live_play_thread.start()
                                if self.output_filename is not None:
                                    reply = 'OK:%s\n' % basename(self.output_filename)
                                else:
                                    reply = 'OK\n'
                                self.output_filename = None
                            elif command == SINGLE_PLAY:
                                self.mode = SINGLE_PLAY
                                self.single_play_thread = Thread(target=self.handle_single_play, name='Single Play', args=args)
                                self.single_play_thread.start()
                                reply = 'OK\n'
                            elif command == JUKEBOX:
                                self.mode = JUKEBOX
                                self.jukebox_thread = Thread(target=self.handle_jukebox, name='Jukebox', args=())
                                self.jukebox_thread.start()
                                reply = 'OK\n'
                            elif command == RESET:
                                self.mode = RESET
                                self.reset_thread = Thread(target=self.handle_reset, name='Reset', args=())
                                self.reset_thread.start()
                                reply = 'OK\n'
                            else:
                                logging.debug('Unknown command %s' % command)
                            logging.debug('Sending reply: %s' % reply.strip())
                            s.sendall(reply)
                        else:
                            logging.debug('Closing command channel connection from %s', s.getpeername())
                            inputs.remove(s)
                            s.close()
                for s in exceptional:
                    logging.debug('Exceptional condition on connection from %s', s.getpeername())
                    inputs.remove(s)
                    s.close()
                if (self.mode == SINGLE_PLAY and not self.single_play_thread.is_alive()) or (self.mode == RESET and not self.reset_thread.is_alive()):
                    # I know, I know, don't repeat yourself...
                    self.mode = LIVE_PLAY
                    self.live_play_thread = Thread(target=self.handle_live_play, name='Live Play', args=())
                    self.live_play_thread.start()
        finally:
            for s in inputs:
                s.close()

    def connect_to_sky_pi(self):
        while True:
            try:
                self.skypi = mido.sockets.connect(SKY_PI_ADDR, SKY_PI_PORT)
                logging.info('Connected to Sky Pi')
                self.skypi.reset()
                break
            except socket.error as e:
                logging.info('Failed to connect to Sky Pi: %s' % e)
                logging.info('Sleeping 3 seconds and trying again.')
                time.sleep(3)

    def handle_reset(self):
        logging.info('Starting reset thread')
        logging.info('Connecting to the sky pi...')
        self.connect_to_sky_pi()
        logging.info('Connected.')
        try:
            self.skypi.reset()
        except socket.error:
            return None

    def handle_live_play(self):
        logging.info('Starting live play thread')
        logging.info('Getting a handle to the sequencer...')
        self.midi_input = self.get_midi_sequencer()
        logging.info('Got sequencer.')
        while True:
            logging.info('Connecting to the Sky Pi...')
            self.connect_to_sky_pi()
            logging.info('Connected.')
            try:
                while True:
                    for event in self.midi_input.iter_pending():
                        logging.debug(repr(event))
                        self.skypi.send(event)
                    if self.mode not in (LIVE_PLAY,RECORD):
                        logging.info('Mode changed to %s, leaving live play thread' % self.mode)
                        if self.skypi:
                            self.skypi.close()
                        return None
                    time.sleep(0.001)
            except socket.error:
                break
            logging.warn('Lost connection to Sky Pi, reconnecting...')

    def handle_single_play(self, song_name):
        logging.info('Starting single play thread for song name %s' % song_name)
        logging.info('Connecting to the sky pi...')
        self.connect_to_sky_pi()
        logging.info('Connected.')
        song_name = slugify(song_name)
        if not song_name.endswith('.mid'):
            song_name = song_name + '.mid'
        filename = os.path.join(JUKEBOX_DIR, song_name)
        if not os.path.isfile(filename):
            logging.info('File %s does not exist, leaving single play thread' % filename)
            return None
        try:
            for event in MidiFile(filename):
                time.sleep(event.time)
                logging.debug(repr(event))
                if not event.is_meta:
                    self.skypi.send(event)
                if self.mode != SINGLE_PLAY:
                    logging.info('Mode changed to %s, leaving single play thread' % self.mode)
                    return None
        except socket.error:
            return None

    def handle_jukebox(self):
        logging.info('Starting jukebox thread')
        logging.info('Connecting to the sky pi...')
        self.connect_to_sky_pi()
        logging.info('Connected.')
        songs = glob.glob(os.path.join(JUKEBOX_DIR, '*.mid'))
        random.shuffle(songs)
        try:
            while True:
                for filename in songs:
                    logging.debug('Playing %s' % os.path.basename(filename))
                    for event in MidiFile(filename):
                        time.sleep(event.time)
                        logging.debug(repr(event))
                        if not event.is_meta:
                            self.skypi.send(event)
                        if self.mode != JUKEBOX:
                            logging.info('Mode changed to %s, leaving jukebox thread' % self.mode)
                            return None
                    logging.debug('Sleeping between songs...')
                    time.sleep(3)
        except socket.error:
            return None

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
        if not os.path.isdir(RECORDING_DIR):
            os.mkdir(RECORDING_DIR)
        self.command_thread = Thread(target=self.handle_command_channel, name='Command', args=())
        self.command_thread.start()
        self.live_play_thread = Thread(target=self.handle_live_play, name='Live Play', args=())
        self.live_play_thread.start()
        self.live_play_thread.join()
        self.command_thread.join()


if __name__ == '__main__':
    s = MIDIServer()
    s.run()
