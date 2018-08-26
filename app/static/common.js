
function activate_button(btnName) {
    var buttons = ['live_play', 'jukebox', 'record', 'unattended'];
    var idx = buttons.indexOf(btnName);
    if (idx > -1) {
        buttons.splice(idx, 1);
    }
    buttons.forEach(function(e) {
        var n = '#' + e;
        $(n).removeClass('btn-primary');
        $(n).removeClass('active');
        $(n).removeAttr('role');
        $(n).removeAttr('aria-pressed');
        if (n == 'record') {
            $('#record').attr('onclick', 'start_record()');
        }
    });
    if (btnName == 'record') {
        $('#' + btnName).addClass('btn-danger');
        $('#' + btnName).text('Stop Recording');
        $('#' + btnName).attr('onclick', 'stop_record()');
    } else {
        $('#' + btnName).addClass('btn-primary');
    }
    $('#' + btnName).addClass('active');
    $('#' + btnName).attr('role', 'button');
    $('#' + btnName).attr('aria-pressed', 'true');
}


function show_alert(text, danger) {
    console.log('Alerting with text "' + text + '"');
    $('#alerty').text(text);
    if (danger) {
        $('#alerty').removeClass('alert-primary');
        $('#alerty').addClass('alert-danger');
    } else {
        $('#alerty').removeClass('alert-danger');
        $('#alerty').addClass('alert-primary');
    }
    $('#alerty').toggleClass('hidden');
    setTimeout(function() { $('#alerty').toggleClass('hidden'); return false; }, 5000);
}

function refresh_song_list() {
    // Refresh the song list
    $.post('/songs', {}).done(function(response) {
        $('#song_list ul').empty();
        response['songs'].forEach(function(song) {
            var song_name = song['name']; 
            if (song_name.endsWith('.mid')) {
                song_name = song_name.replace('.mid', '');
            }
            $('#song_list ul').append('<li class="list-group-item"><a href="#" class="songlink">' + song_name + '</a></li>');
        });
        $('a.songlink').click(function() { single_play(this.text); });
    }).fail(function(response) {
        show_alert('Failed to refresh song list: ' + response['reason'], true);
    });
}
