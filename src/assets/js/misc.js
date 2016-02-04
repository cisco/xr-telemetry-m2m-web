/*
 * ============================================================================
 * misc.js
 *
 * This file implements miscellaneous functionality.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */
//
// Generic bits of functionality
//

$(function () { // on document load

    //
    // Simply ajaxify any forms with the 'ajax_form' class
    //
    $('.ajax_form').each(function () {
        $(this).ajaxForm();
    });

    //
    // Hide all the spinners at start
    //
    $('.spinner').each(function () {
    	$(this).css('visibility', 'hidden');
    });

    //
    // Focus on text boxes when tabs selected
    //
    function give_element_focus_on_click(tab_link, to_focus_id) {
        $('a[href$="#' + tab_link + '"]').click(function() {
            // Need to wait 1ms because otherwise the tab link seems
            // to retain the focus
            window.setTimeout(function() {
                $('#' + to_focus_id).focus();
            }, 1);
        });
    }
    give_element_focus_on_click("simple_cli", "simple_cli_input");
    give_element_focus_on_click("json_cli", "json_cli_input");
    give_element_focus_on_click("get", "get_input");
    give_element_focus_on_click("schema", "schema_input");
    give_element_focus_on_click("script", "script_box");
    give_element_focus_on_click("gpb", "gpb_path");
});
