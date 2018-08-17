# TODO

## Sky Pi
* -Fix missing note-off events, pickling failures when data comes too quick-
    * -Use mido's PortServer-

## MIDI Server
* See if logging module can automatically rotate at size threshold
* -Add command to play specified songs-
* -Add command to start playing all songs in `JUKEBOX_DIR` in random order-
* Limit note octaves to -1..1
* Ignore control change events from volume slider, other buttons
    * Pass pitch/modulation control messages through

## Jukebox
* -Make song links on index page start playing that song when clicked-

## UI
* Refresh song list after Stop Recording button pressed
* Clear modal dialog fields after use
* -Make `temp_name` field hidden-
* Add unattended-mode page that is single-play only
* Move docent page to a different URL
* Make alert div actually show and automatically dismiss
    * Might need to use `setTimeout()`
    * Also look into `$('#alerty').alert()`; see [Bootstrap docs on alerts](https://getbootstrap.com/docs/4.0/components/alerts/)
* Strip `.mid` suffix from song names when displaying on main page
* Add panic button that shuts off all notes and sends control messages to reset everything
* -Fix scrunched look-

## Backend
* Systemd unit files for daemons
* Password changes on production Pis
* Port knocking for SSH?

## Nice to have
* Autodiscovery of hostnames (Avahi)
* Nice offset background image of John Hollis' art
* "Next" button in Jukebox mode
