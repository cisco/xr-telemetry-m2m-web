/*
 * ============================================================================
 * get.js
 *
 * This file contains code pertaining to the `get` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {

// On page load
$(function () {
    // Give get path box autocomplete
    $('#get_input').autocomplete({
        autoFocus: true,
        minLength: 0,
        source: M2M.path_autocomplete_source
    });
})

})(M2M, jQuery);
