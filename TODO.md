# TODO

## MIDI Server
* Add command to play specified songs
* Add command to start playing all songs in `JUKEBOX_DIR` in random order
* Limit note octaves to -1..1
* Ignore control change events from volume slider, other buttons
    * Pass pitch/modulation control messages through

## Jukebox
* Make song links on index page start playing that song when clicked

## UI
* Add unattended-mode page that is jukebox only
* Move docent page to a different URL
* Make alert div actually show and automatically dismiss
    * Might need to use `setTimeout()`
    * Also look into `$('#alerty').alert()`; see [Bootstrap docs on alerts](https://getbootstrap.com/docs/4.0/components/alerts/)
* Strip `.mid` suffix from song names when displaying on main page
* Add panic button that shuts off all notes and sends control messages to reset everything

