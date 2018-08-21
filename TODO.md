# TODO

## Sky Pi
* ~~Fix missing note-off events, pickling failures when data comes too quick~~
    * ~~Use mido's PortServer~~

## MIDI Server
* Mode command should report song being played in jukebox and single play modes
* ~~Automatically rotate logs at size threshold~~
* ~~Add command to play specified songs~~
* ~~Add command to start playing all songs in `JUKEBOX_DIR` in random order~~
* ~~Limit note octaves to -1..1~~ _(went with -1..+5, configurable)_
* ~~Ignore control change events from volume slider, other buttons, Pass pitch/modulation control messages through~~
* ~~Set program to tubas on connect~~
    * ~~Code exists, disabled by config because it doesn't work on my setup. Need to test on the Roland and Roger's synth.~~
    * _No longer needed; program change control messages are dropped on the mud pi._

## Jukebox
* ~~Make song links on index page start playing that song when clicked~~

## UI
* Add unattended-mode page that is single-play only
* Move docent page to a different URL
* Make alert div actually show and automatically dismiss
    * Might need to use `setTimeout()`
    * Also look into `$('#alerty').alert()`; see [Bootstrap docs on alerts](https://getbootstrap.com/docs/4.0/components/alerts/)
    * Fix it so it comes up with the right color at the right time
    * Probably easiest to refactor to a method
* ~~Add reboot button~~
* ~~Refresh song list after Stop Recording button pressed~~
* ~~Clear modal dialog fields after use~~
* ~~Make `temp_name` field hidden~~
* ~~Strip `.mid` suffix from song names when displaying on main page~~
* ~~Add panic button that shuts off all notes and sends control messages to reset everything~~
    * _Button restarts midiserver_.
* ~~Fix scrunched look~~
* ~~Download jQuery, Bootstrap and make sure app uses local copies instead of CDN~~

## Backend
* ~~Systemd unit files for daemons~~
* Password changes on production Pis
* Port knocking for SSH?

## Nice to have
* Autodiscovery of hostnames (Avahi)
* Nice offset background image of John Hollis' art
* "Next" button in Jukebox mode
