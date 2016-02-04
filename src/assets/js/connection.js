/*
 * ============================================================================
 * connection.js
 *
 * This file contains code pertaining to the `Connection` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {

var previous_state = 'disconnected';

//
// Connection status changing (disconnected/connecting/connected)
//
function handle_connection_state(v) {
    // set the connection-state text content
    $('#connection_status').html(v.state);

    // set the color of the connection-state text
    if (v.state === 'connected') {
        $('#connection_status').removeClass('not_connected');
    } else {
        $('#connection_status').addClass('not_connected');
    }

    // grey out the form and display the disconnect button when appropriate
    if (v.state === 'disconnected') {
        $('#connection_fieldset').prop('disabled', false);
        $('#disconnect').css('display', 'none');
        if (previous_state === 'connected') {
            alert("Connection to router lost");
        }
    } else {
        $('#connection_fieldset').prop('disabled', 'disabled');
        $('#disconnect').css('display', 'inline');
    }

    // display the spinner when appropriate
    if (v.state === 'connecting') {
        $('#connection_loader').show();
    } else {
        $('#connection_loader').hide();
    }

    previous_state = v.state;
}


$(function () { // on document load
    //
    // Ajaxify the connection form
    //
    var connect_options = {
        beforeSubmit: setup_connection_form
    };
    function setup_connection_form() {
        // Clear the last error message and close the credentials
        // box when you kick off a new connection attempt
        $('#connection_failure_reason').text('');
        if ($('#creds').css('display') !== 'none') {
            $('#creds').slideToggle();
        }
    }
    $('#start_connection').ajaxForm(connect_options);

    //
    // Handle the disconnect button being invoked
    //
    $('#disconnect').click(function () {
        previous_state = 'connecting'; // avoid alert when we reach disconnected state
        $.post('connection', {'disconnect': true}, function () {
            console.log('requested disconnection');
        });
    });

    //
    // Enable connection credentials panel toggling
    //
    $('#toggle_creds').click(function (e) {
        $('#creds').slideToggle();
        e.preventDefault();
    });
});

M2M.handler["connection_state"] = handle_connection_state;

})(M2M, jQuery);
