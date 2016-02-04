/*
 * ============================================================================
 * _tabs.js
 *
 * This file implements the infrastructure for switching between the various
 * tabs, including the per-tab debug sections.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

M2M = M2M || {};
(function (M2M, $) {

//
// Handle initialization of tabs.
//
var tab_init = {};
function tab_init_fn(tab) {
    // Not all tabs will have an init function registered, so check before
    // blindly attempting the call.
    if (tab in tab_init) {
        tab_init[tab]();
    }
}

//
// Getter function for the current tab.
//
var current_tab = "";
function get_current_tab() {
    return current_tab;
}

//
// Either return a function to toggle the debug panel for, or
// disable the button
//
function create_debug_toggle_lambda(selector) {
    var sel = $(selector);
    var btn = $('#toggle_debug');
    if (sel.length) {
        // this tab has a debug panel div
        btn.removeClass('disabled');
        return function () {
            sel.slideToggle();
        };
    } else {
        // no debug panel for this tab, so grey out the button
        btn.addClass('disabled');
    }
}

function on_telemetry_select() {
    var $explorer_tab = $("a[href$='explorer']");
    var $explorer_content = $($explorer_tab[0].hash);
    var $explorer_explanation = $("#explorer_form_explanation");
    var $explorer_display = $("#explorer_display");
    var $explorer_wrapper = $("#explorer_wrapper");
    var $explorer_body = $("#explorer_body");
    var $explorer_show_hide = $("#explorer_show_hide");
    var $explorer_show_hide_button = $("#explorer_show_hide_button");

    // Show explorer in telemetry tab
    $explorer_content.show();
    // With explanation message
    $explorer_explanation.show();
    // But don't show the explorer display, just the paths
    $explorer_display.hide()
    // And make it scrollable by fixing its height
    $explorer_wrapper.css("height", "600px");
    // Show body only if button says "Hide" (i.e. does not say "Show")
    if ($explorer_show_hide_button.html() === M2M.explorer_button_show_label) {
        $explorer_body.hide();
    } else { // should equal M2M.explorer_button_hide_label
        $explorer_body.show();
    }
    // Show show/hide button
    $explorer_show_hide.show();
}

function on_explorer_select() {
    var $explorer_display = $("#explorer_display");
    var $explorer_explanation = $("#explorer_form_explanation");
    var $explorer_wrapper = $("#explorer_wrapper");
    var $explorer_body = $("#explorer_body");
    var $explorer_show_hide = $("#explorer_show_hide");

    // Make sure explorer display is shown
    $explorer_display.show();
    // Without the telemetry tab explanation
    $explorer_explanation.hide();
    // And we don't want it scrollable, so don't fix its height
    $explorer_wrapper.css("height", "");
    // Definitely show body
    $explorer_body.show();
    // But not show/hide button
    $explorer_show_hide.hide();
}

$(function () { // on document load

    //
    // Add a starting debug click handler (overwritten below) - this
    // cheesily knows which tab opens at start.
    //
    $('#toggle_debug').click(create_debug_toggle_lambda('#connection_debug'));

    // Ensure that explorer appears on the right of the telemetry tab
    // by moving telemetry div to top of list of divs in main div
    $('.main').prepend($('#telemetry'));
    // Also set telemetry:explorer ratio
    $('#telemetry').css('width', '65%');
    // And hide the schema browser (also binds button)
    M2M.explorer_button_hide();

    //
    // Manage the main tabs
    //
    $('.nav ul').each(function () {
        // For each set of tabs, we want to keep track of
        // which tab is active and its associated content
        var $active, $content, $links = $(this).find('a');

        // If the location.hash matches one of the links, use that as the active tab.
        // If no match is found, use the first link as the initial active tab.
        $active = $($links.filter('[href="' + location.hash + '"]')[0] || $links[0]);
        $active.addClass('active');

        current_tab = $active.attr('href').substring(1);

        $content = $($active[0].hash);

        // Hide the remaining content
        $links.not($active).each(function () {
            $(this.hash).hide();
        });

        // Bind the click event handler
        $(this).on('click', 'a', function (e) {
            var $explorer_tab, $explorer_content;

            current_tab = this.getAttribute('href').substring(1);

            // Make the old tab inactive.
            $active.removeClass('active');
            $content.hide();

            // Update the variables with the new link and content
            $active = $(this);
            $content = $(this.hash);

            // Make the tab active.
            $active.addClass('active');
            $content.show();

            // Hack to get the schema explorer onto the telemetry tab
            if (current_tab === 'telemetry') {
                on_telemetry_select();
            } else if (current_tab === 'explorer') {
                on_explorer_select();
            } else {
                $explorer_tab = $("a[href$='explorer']");
                $explorer_content = $($explorer_tab[0].hash);
                $explorer_content.hide();
            }

            // Make the 'toggle debug' button apply to this tab
            $('#toggle_debug').unbind('click').click(
                create_debug_toggle_lambda($active.attr('href') + '_debug')
            ); 

            // Call the new tab's init function.
            tab_init_fn(current_tab);

            // Prevent the anchor's default click action
            e.preventDefault();
        });
    });
});

//
// Public API.
//
M2M.tab = {
    "init":    tab_init,
    "current": get_current_tab
};

})(M2M, jQuery);
