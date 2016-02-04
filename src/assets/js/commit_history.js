/*
 * ============================================================================
 * commit_history.js
 *
 * This file contains code pertaining to the `Commit History` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {
    function handle_commit_history_updates () {
        $('#cfg_hist_output button').click(function (e) {
            var row_sel = "#subrow_" + this.id.split("_")[1];
            $(row_sel).toggle();
        });

        var last_id = $('#cfg_hist_output table tr:eq(1) td:eq(2)').html()
        $('#history form input').click(function (e) {
            $.post('history', {'last_id': last_id});
            e.preventDefault();
        });
    }

    M2M.handler["commit_history_updates"] = handle_commit_history_updates;
})(M2M, jQuery);
