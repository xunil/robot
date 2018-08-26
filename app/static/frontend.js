// Front end Javascript for the Robot

function get_current_mode() {
    $.get('/mode').done(function(response) {
        activate_button(response['mode']);
    }).fail(function(response) {
        show_alert('Failed to get current mode: ' + response['reason'], true);
    });
}

function rename_song() {
    $.post('/rename', {"old": $('#temp_name').val(), "new": $('#song_name').val()}).done(function(response) {
        $('#songNameModal').modal('hide');
        show_alert('Saved recording as <strong>' + response['reason'] + '</strong>', false);
    }).fail(function(response) {
        $('#songNameModal').modal('hide');
        show_alert('Failed to rename recording: ' + response['reason'], true);
    });
    // Clear values from last recording
    $('#temp_name').val("");
    $('#song_name').val("");
    refresh_song_list();
}

function start_record() {
    $.post('/start_record', {}).done(function(response) {
        activate_button('record');
    }).fail(function() {
        show_alert('Failed to start recording: ' + response['reason'], true);
    });
}

// TODO: Detect that recording is in progress and call this function
// if another button (Jukebox, Live Play) is clicked instead of the
// Stop Recording button.
function stop_record() {
    $.post('/stop_record', {}).done(function(response) {
        activate_button('live_play');
        $('#record').removeClass('btn-danger');
        $('#record').text('Record');
        $('#record').attr('onclick', 'start_record()');
        console.log(JSON.stringify(response));
        $('#temp_name').val(response['filename']);
        $('#songNameModal').modal('show');
    }).fail(function(response) {
        show_alert('Failed to stop recording: ' + response['reason'], true);
    });
}

function start_jukebox() {
    $.post('/jukebox', {}).done(function(response) {
        activate_button('jukebox');
    }).fail(function(response) {
        show_alert('Failed to start Jukebox: ' + response['reason'], true);
    });
}

function start_live_play() {
    $.post('/live_play', {}).done(function(response) {
        activate_button('live_play');
    }).fail(function(response) {
        show_alert('Failed to start Live Play: ' + response['reason'], true);
    });
}

function single_play(song_name) {
    console.log(JSON.stringify(song_name));
    $.post('/single_play', {"song_name": song_name}).done(function(response) {
        console.log(JSON.stringify(response));
    }).fail(function(response) {
        console.log(JSON.stringify(response));
        show_alert('Failed to play song: ' + response['reason'], true);
    });
}

function start_reset() {
    $.post('/reset', {}).done(function(response) {
        start_live_play();
    }).fail(function() {
        $('#derp').text('Failed');
    });
}

function start_unattended() {
    $.post('/unattended', {}).done(function(response) {
        get_current_mode();
    }).fail(function(response) {
        show_alert('Failed to start unattended mode: ' + response['reason'], true);
    });
}

function start_panic() {
    $.post('/panic', {}).done(function(response) {
        show_alert('Restarted services successfully.', false);
        start_live_play();
    }).fail(function() {
        show_alert('Failed to restart services!', true);
    });
}

function start_reboot() {
    $.post('/rebootay', {}).done(function(response) {
        show_alert('Rebooting.', false);
    }).fail(function() {
        show_alert('Failed to reboot!', true);
    });
}

function start_poweroff() {
    $.post('/lightsout', {}).done(function(response) {
        show_alert('Powering off.', false);
    }).fail(function() {
        show_alert('Failed to reboot!', true);
    });
}

