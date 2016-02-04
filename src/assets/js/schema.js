/*
 * ============================================================================
 * schema.js
 *
 * This file contains miscellaneous schema-related functionality.
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
    // Give schema path box autocomplete
    $('#schema_input').autocomplete({
        autoFocus: true,
        minLength: 0,
        source: M2M.path_autocomplete_source
    });
})

})(M2M, jQuery);
