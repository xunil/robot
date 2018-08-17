import sys
import socket
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))
from config import *

# Methods for connecting to the midiserver command channel
def command(cmd, *args):
    try:
        cmdsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cmdsock.connect(('127.0.0.1', CMD_PORT))
        print >>sys.stderr, '-- COMMAND -- Sending command %s' % (':'.join([cmd] + list(args)))
        cmdsock.sendall('%s\n' % (':'.join([cmd] + list(args))))
        reply = cmdsock.recv(4096)
        reply = reply.strip()
        print >>sys.stderr, '-- COMMAND -- Received reply %s' % reply
    except socket.error as e:
        return (False, list(str(e)))
    finally:
        cmdsock.close()
    return (True, reply.split(':'))
