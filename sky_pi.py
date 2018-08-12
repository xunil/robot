#!/usr/bin/env python
import mido
import os
import cPickle as pickle
import socket
import sys

client_name = 'CH345'
client_found = False

for port_name in mido.get_output_names():
    if port_name.split(':')[0] == client_name:
        client_name = port_name
        client_found = True
        break

if not client_found:
    print >>sys.stderr, 'Could not find client named %s' % client_name
    os.exit(1)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('0.0.0.0', 23840)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)
sock.listen(1)


while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()
    connection.setblocking(1)
    print connection
    try:
        print >>sys.stderr, 'connection from', client_address

        with mido.open_output(client_name) as midi_out:
            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(4096)
                print >>sys.stderr, 'received %d bytes' % len(data)
                if data:
                    try:
                        event = pickle.loads(data)
                        if event:
                            # print >>sys.stderr, event
                            midi_out.send(event)
                    except pickle.UnpicklingError as e:
                        print >>sys.stderr, 'could not unpickle that: %s.' % str(e)
                else:
                    print >>sys.stderr, 'no more data from', client_address
                    break
            
    finally:
        # Clean up the connection
        connection.close()