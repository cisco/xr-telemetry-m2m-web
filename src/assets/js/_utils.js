/*
 * ============================================================================
 * _utils.js
 *
 * This file contains various utility functions.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {

//
// Convert a JSON object into pretty-printed string.
//
function prettify(stuff) {
    return JSON.stringify(stuff, null, 2);
}

//
// Show the progress 'spinner' while a request is in progress.
//
function spinner_on(tab) {
    console.log("Spinner on: " + tab);
    $("#spinner_" + tab).css('visibility', 'visible');
}

//
// Hide the progress 'spinner' when the request is complete.
//
function spinner_off(tab) {
    console.log("Spinner off: " + tab);
    $("#spinner_" + tab).css('visibility', 'hidden');
}

M2M.utils = {
    "prettify":    prettify,
    "spinner_on":  spinner_on,
    "spinner_off": spinner_off
};

})(M2M, jQuery);
