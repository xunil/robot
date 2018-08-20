# TODO: Connect the fancier M-Audio and get its ID
MIDI_CLIENT_NAMES = ['Keystation 49', 'Keystation 61']

# TODO: Use avahi
# Network configuration
SKY_PI_ADDR = '192.168.2.49'
SKY_PI_PORT = 23840
CMD_PORT = 23850

# Modes
LIVE_PLAY = 'live_play'
JUKEBOX = 'jukebox'
RECORD = 'record'
MODE = 'mode'
SINGLE_PLAY = 'single_play'
RESET = 'reset'

# MIDI filtering configuration
MIN_OCTAVE = 2
MAX_OCTAVE = 7

# MIDI event types
NOTE_ON = 'note_on'
NOTE_OFF = 'note_off'
CONTROL_CHANGE = 'control_change'
PROGRAM_CHANGE = 'program_change'
PITCH_WHEEL = 'pitchwheel'
# MIDI control number
MODULATION_WHEEL = 1

DEFAULT_PROGRAM = 58 # Tuba

SET_DEFAULT_PROGRAM_ON_CONNECT = False

# Where to store files
RECORDING_DIR = '/home/pi/recordings'
JUKEBOX_DIR = '/home/pi/jukebox'
