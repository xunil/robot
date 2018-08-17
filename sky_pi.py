#!/usr/bin/env python
import mido
import os
# import cPickle as pickle
import socket
import sys

from config import *

client_names = ['CH345', 'UM-1SX']
client_found = False
selected_client = None

for port_name in mido.get_output_names():
    if port_name.split(':')[0] in client_names:
        selected_client = port_name
        client_found = True
        break

if not client_found:
    print >>sys.stderr, 'Could not find client named %s' % selected_client
    sys.exit(1)

with mido.sockets.PortServer('0.0.0.0', 23840) as server:
    with mido.open_output(selected_client) as midi_out:
        while True:
            connection = server.accept()
            for event in connection:
                print >>sys.stderr, event
                midi_out.send(event)
