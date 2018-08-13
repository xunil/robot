

def midiserver_command(command):
    try:
        cmd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cmd.connect((SKY_PI_ADDR, SKY_PI_PORT))
        cmd.sendall('%s\n' % command)
        reply = cmd.recv(4096)
        reply = reply.strip()
    except socket.error as e:
        return (False, list(str(e)))
    finally:
        cmd.close()
    return (True, reply.split(':'))
