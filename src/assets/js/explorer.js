/*
 * ============================================================================
 * explorer.js
 *
 * This file contains code pertaining to the `explorer` tab.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {

var tab = "explorer",
    initialized = false,
    schema_db = {},
    root;

var recommended_paths = [ // from http://enwiki.cisco.com/eXR/Telemetry/UserGuide#Supported_Paths
    "RootOper.Interfaces.Interface",
    "RootOper.InfraStatistics.Interface.Latest.GenericCounters",
    "RootOper.InfraStatistics.Interface.Latest.DataRate",
    "RootOper.InfraStatistics.Interface.Latest.Protocol",
    "RootOper.PlatformInventory.Rack.Attributes.BasicInfo",
    "RootOper.PlatformInventory.Rack.Slot.Card.Sensor.Attributes.BasicInfo",
    "RootOper.MPLS_TE.Tunnels.TunnelAutoBandwidth",
    "RootOper.MPLS_TE.P2P_P2MPTunnel.TunnelHead",
    "RootOper.MPLS_TE.SignallingCounters.HeadSignallingCounters",
    "RootOper.BGP.Instance.InstanceActive.DefaultVRF.Neighbor",
    "RootOper.QOS.Interface.Input.Statistics",
    "RootOper.QOS.Interface.Output.Statistics",
 ]

function prune(path) {
    var index = path.lastIndexOf(".");
    return path.substring(index + 1);
}

function display(path) {
    var data = {};
    for (var key in schema_db[path]) {
        if (key !== "children") {
            data[key] = schema_db[path][key];
        }
    }
    $('#explorer_display').html(M2M.utils.prettify(data));

    // Set active path box in policy web form to clicked-on path
    if (!$('#telemetry').is(':hidden')) { //  (only if telemetry tab not hidden)
        M2M.$active_path_box.val(path);
    }

    hljs.highlightBlock(document.getElementById("explorer_display"));
}

function add_child(elem, path) {
    var li = document.createElement("li"),
        a  = document.createElement("a");

    a.innerHTML = prune(path);
    a.href = "#";

    li.id = path;
    li.className = (!(path in schema_db) || schema_db[path].children.length > 0)
        ? "expandable" : "inert";
    li.appendChild(a);

    // If path is recommended then show it visually
    li.style.fontWeight = 'normal'; // Don't inherit parent's boldness
    recommended_paths.forEach(function(recommended_path) {
        if (path_is_prefix_of(path, recommended_path)) {
            li.style.fontWeight = 'bold';
        }
        if (path === recommended_path) {
            li.style.color = 'green';
        }
    });

    elem.appendChild(li);
}

function add_children(elem, children) {
    var ul = document.createElement("ul");

    elem.appendChild(ul);
    children.forEach(function (child) {
        add_child(ul, child);
    });
}

function expand(elem) {
    var children = get_children(schema_db[elem.id]);
    add_children(elem, children);
    elem.className = "collapsible";
}

function collapse(elem) {
    var child = elem.getElementsByTagName("ul")[0];
    elem.removeChild(child);
    elem.className = "expandable";
}

function get_schemas(paths) {
    // We only want to query the server for those paths which we don't already
    // have the schema stored in the database.
    var missing = paths.filter(function (path) {
        return !(path in schema_db);
    });
    if (missing.length > 0) {
        M2M.request(tab, {"paths": missing});
        M2M.utils.spinner_on(tab);
    }
}

function click_handler(e) {
    var elem = (e.target || e.srcElement).parentNode,
        children;

    // The event listener for which this is the callback is attached to a 'div'
    // element, but we only want to try to do an expansion when one of the
    // links has been clicked.
    if (elem.tagName === "LI") {
        if (elem.classList.contains("expandable")) {
            expand(elem);
        } else if (elem.classList.contains("collapsible")) {
            collapse(elem);
        }
        children = get_children(schema_db[elem.id]);
        get_schemas(children);
        display(elem.id);

        e.preventDefault();
        e.stopPropagation();
    }
}

function path_is_prefix_of(prefix, s) {
    // Can't just use s.indexOf(prefix) === 0 because this would
    // return true for say RootOper.Platform with RootOper.PlatformInventory
    var pre_sections, s_sections, i;
    pre_sections = prefix.split(".");
    s_sections = s.split(".");
    // Prefix must not be longer than s
    if (s_sections.length < pre_sections.length) {
        return false;
    }
    // Each component must match
    for (i = 0; i < pre_sections.length; i++) {
        if (pre_sections[i] !== s_sections[i]) {
            return false;
        }
    }
    return true;
}

function order_paths(a, b) {
    var a_recommended = false,
        b_recommended = false;

    // Determine if either of `a` and `b` are prefixes of recommended paths.
    recommended_paths.forEach(function(rec_path) {
        if (!a_recommended) {
            a_recommended = path_is_prefix_of(a, rec_path);
        }
        if (!b_recommended) {
            b_recommended = path_is_prefix_of(b, rec_path);
        }
    });

    // If both `a` and `b` are recommended, or if neither are recommended, then
    // return the result of direct string comparison. Otherwise return the
    // recommended path as belonging before the non-recommended path.
    if (a_recommended === b_recommended) {
        return a.toLowerCase().localeCompare(b.toLowerCase());
    } else if (a_recommended) {
        return -1;
    } else if (b_recommended) {
        return +1;
    }
}

function get_children(path) {
    // Return the (sorted) children of the given path.
    return path.children.sort(order_paths);
}

function handle_explorer(data) {
    var schemas;

    try {
        schemas = JSON.parse(data.text);
        for (var path in schemas) {
            schema_db[path] = schemas[path];
            var elem = document.getElementById(path);
            if (elem) { // might not exist yet if this is an autocomplete request
                elem.className = (schemas[path].children.length > 0) ? "expandable" : "inert";
            }
        }
    } catch (e) {
        console.log(e);
    }

    M2M.utils.spinner_off(tab);
}

// On page load populate the explorer root node with some example paths and
// attach an event handler to prevent each child element needing to have their
// own.
$(function () {
    root = document.getElementById("explorer_root");
    root.addEventListener("click", click_handler, false);
});

function init() {
    var paths = ["RootOper", "RootCfg"];
    if (!initialized) {
        get_schemas(paths);
        add_children(root, paths);
        initialized = true;
    }
}

/* Functions relating to the explorer schema show/hide button for telemetry tab */
function explorer_button_show() {
    $('#explorer_body').show();
    $('#explorer_title').show();
    $('#telemetry').css('width', '65%');
    $('#explorer_show_hide_button').html(M2M.explorer_button_hide_label)
        .off('click') // removes the old binding
        .click(M2M.explorer_button_hide);
}

function explorer_button_hide() {
    $('#explorer_body').hide();
    $('#explorer_title').hide();
    $('#telemetry').css('width', '83%');
    $('#explorer_show_hide_button').html(M2M.explorer_button_show_label)
        .off('click') // removes the old binding
        .click(M2M.explorer_button_show);
}

/* Functions relating to autocomplete */
function get_cached_paths() {
    var cached_paths = ["RootOper", "RootCfg"]; // These do not appear as children
    for (var path in schema_db) {
        cached_paths = cached_paths.concat(get_children(schema_db[path]));
    }
    return cached_paths;
}

function add_children_to_cache(parent) {
    if (parent in schema_db) {
        get_schemas(get_children(schema_db[parent])); // fetch children
    } else { // fetch all ancestors (but not children because we don't know their paths)
        var ancestors = [];
        var sections = parent.split('.');
        for (var i = 1; i < sections.length; i++) {
            ancestors.push(sections.slice(0, i).join('.'));
        }
        get_schemas(ancestors);
    }
}

//
// Public API.
//
M2M.handler["explorer"] = handle_explorer;
["explorer", "telemetry", "gpb", "schema", "get"].forEach(function(tab) {
    // All tabs that autocomplete paths need this init
    M2M.tab.init[tab] = init;
})

M2M.explorer_button_show = explorer_button_show;
M2M.explorer_button_hide = explorer_button_hide;
M2M.explorer_button_show_label = "Show Schema Explorer";
M2M.explorer_button_hide_label = "Hide";
M2M.get_cached_paths = get_cached_paths;
M2M.add_children_to_cache = add_children_to_cache;
M2M.order_paths = order_paths;

})(M2M, jQuery);
