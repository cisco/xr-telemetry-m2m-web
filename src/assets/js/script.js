/*
 * ============================================================================
 * script.js
 *
 * This file contains code pertaining to the `Script` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {

// An object to hold the pre-written example scripts. These are keyed using a
// url hash.
var scripts = {}

//
// Load a pre-written script into the page.
//
function load_script(script) {
    var elem = document.getElementById('script_box');
    elem.value = scripts[script];
}

// Bind event handlers for the script loaders on page load.
$(function () {
    // Load up the scriptlets 
    $.get('scriptlets', {}, function (s) {
        console.log('got scriptlets:' + JSON.stringify(Object.keys(s)));
        for (var script in s) {
            scripts[script] = s[script];
        }
    });

    $('.script_loader ul').each(function () {
        $(this).on('click', 'a', function (e) {
            var script = this.href.split('#')[1];
            console.log(script);
            load_script(script);
            e.preventDefault();
        });
    });
});

})(M2M, jQuery);
