/*
 * ============================================================================
 * _comms.js
 *
 * This file implements the infrastructure for communicating between client
 * and server.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {

var handler = {};

//
// Send a POST request to the server.
//
function request(tab, data) {
    $.post(tab, data);
};

//
// Initiate the repetitive pull of JSON updates from the server, and dispatch
// each one individually.
//
// @@@ Note that this isn't currently safe with multiple browser tabs
//
function get_push_queue() {
    var fn;
    $.post('push_queue', {}, function (push_queue) {
        push_queue.forEach(function (elem) {
            if (elem.fn.indexOf("handle_") === 0) {
                fn = elem.fn.replace("handle_", "")
                if (fn in handler) {
                    console.log("Received message from server, calling handler \"" + fn + "\"");
                    handler[fn](elem);
                } else {
                    alert("Unable to call handler " + fn);
                }
            } else {
                console.log("Refusing to dispatch " + JSON.stringify(elem));
            }
        });

        // We want to poll the server "constantly" so fire off another request
        // as soon as we've finished handling the previous one. Use setTimeout
        // to avoid infinite recursion.
        setTimeout(get_push_queue, 0);
    });
}

// Begin polling the server on page load completion.
$(get_push_queue);


//
// Add a few generic services that are used several times. Each of
// these has its own SessionData method in session.py on the server
// side.
//

//
// Update some element's text content
//
function handle_set_text(v) {
    $(v.selector).text(v.text);
}

//
// Update some element's html
//
function handle_set_html(v) {
    $(v.selector).html(v.html);
}

//
// Log to console
//
function handle_log(v) {
    console.log(v.msg);
}

//
// Alert
//
function handle_alert(v) {
    alert(v.msg);
}

//
// Syntax highlight an element
//
function handle_highlight(v) {
    $(v.selector).each(function(i, elem) {
        hljs.highlightBlock(elem);
    });
}

//
// Stop current spinner
//
function handle_spinner(v) {
    var tab = M2M.tab.current();
    M2M.utils.spinner_off(tab);
}

handler = {
    "set_text":             handle_set_text,
    "set_html":             handle_set_html,
    "log":                  handle_log,
    "alert":                handle_alert,
    "highlight":            handle_highlight,
    "stop_current_spinner": handle_spinner
};

//
// Public API
//
M2M.handler = handler;
M2M.request = request;

})(M2M, jQuery);
