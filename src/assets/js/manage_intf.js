/*
 * ============================================================================
 * manage_intf.js
 *
 * This file contains code pertaining to the `Manage Interface` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var pending_update = false;

function update_json () {
    pending_update = true;
    setTimeout(function () { 
        if (pending_update) {
            $('#update_json_input').trigger('click');
            pending_update = false;
        }
    }, 10);
}

$(function () {
    $('#manage_intf input').keypress(update_json).keydown(update_json);
    $('#manage_intf textarea').keypress(update_json).keydown(update_json);
    setTimeout(update_json, 1000); // bit cheesy
});
