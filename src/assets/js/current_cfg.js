/*
 * ============================================================================
 * current_config.js
 *
 * This file contains code pertaining to the `Current Config` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {
    // Track the visibility of the various parts of the mapping.
    var VISIBLE = {
        "cli": true,
        "path": true,
        "value": true
    };

    // Find the checkbox element for the given part.
    function checkbox(part) {
        return $("input[type='checkbox'][name='toggle_" + part + "']");
    }

    // Update the visibility of the given part.
    function update(part) {
        var elem = $("#current_config_result ." + part);
        VISIBLE[part] ? elem.show() : elem.hide();
    }

    // Create an event handler for toggling the visibility of the given part.
    function handler(part) {
        return function () {
            VISIBLE[part] = this.checked;
            update(part);
        };
    }

    // On page load bind event handlers to the visibility checkboxes.
    $(function () {
        for (var part in VISIBLE) {
            checkbox(part).change(handler(part));
        }
    });

    // Display the latest progress updates.
    function progress(msg) {
        $("#current_config_progress").html(msg.progress);
    }

    // Update the visibility of the various parts of the mapping once complete.
    function loaded() {
        // Hide progress now that mapping is complete. 
        $("#current_config_progress").html("");

        for (var part in VISIBLE) {
            update(part);
        }
    }

    M2M.handler["current_cfg_progress"] = progress;
    M2M.handler["current_cfg_loaded"] = loaded;
})(M2M, jQuery);
