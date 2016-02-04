/*
 * ============================================================================
 * features.js
 *
 * This file contains code pertaining to the `features` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M) {
"use strict";

function checkbox_change_handler(checkbox) {
    // Find the link corresponding to the value of the changed checkbox
    // and enable/disable it as appropriate.
    var link = document.querySelector(
        "ul#feature-links a[href='#" + checkbox.value + "']");
    link.parentNode.hidden = !checkbox.checked;
}

function init() {
    var features = document.getElementById("features"),
        checkboxes = features.getElementsByTagName("input");

    // Trigger the change handler on each checkbox to ensure that the
    // links are correctly enabled/disabled initially.
    for (var i = 0; i < checkboxes.length; i++) {
        checkbox_change_handler(checkboxes[i]);
    }

    // Bind the event listener to the parent element which contains the
    // checkboxes.
    features.addEventListener("change", function (e) {
        // Only trigger the change event handler if a checkbox has
        // actually been changed.
        if (e.target.tagName === "INPUT") {
            checkbox_change_handler(e.target);
        }

        // Prevent this event bubbling.
        e.stopPropagation();
    }, false);
}

window.addEventListener("load", init, false);

})(M2M);
