/*
 * ============================================================================
 * request.js
 *
 * This file implements the infrastructure behind the various request wrapper
 * tabs.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M, $) {

var history = {};

//
// Handle receiving confirmation of the request triggered on the server.
//
function handle_request(data) {
    var request = JSON.parse(data.text);
    history[request.id] = {
        'status':  'pending',
        'request': M2M.utils.prettify(request),
        'reply':   {}
    };
    M2M.utils.spinner_on(M2M.tab.current());
}

//
// Handle receiving a reply from the server.
//
function handle_reply(tab) {
    return function (data) {
        var elem_success = document.getElementById(tab + '_success'),
            elem_result  = document.getElementById(tab + '_result'),
            reply, success, result;

        try {
            reply = JSON.parse(data.text);

            history[reply.id].status = 'complete';
            history[reply.id].reply = M2M.utils.prettify(reply);

            if ('result' in reply) {
                success = true;
                result = (tab === 'simple_cli') ? reply.result
                                                : M2M.utils.prettify(reply.result);
            } else if ('error' in reply) {
                success = false;
                result = M2M.utils.prettify(reply.error);
            } else {
                success = false;
                result = 'Invalid reply from server: ' + data.text;
            }
        } catch (e) {
            success = false;
            result = 'Error parsing JSON: ' + data + ', error: ' + e;
        }

        elem_success.innerHTML = success ? 'Success' : 'Error';
        elem_result.innerHTML  = result;

        M2M.debug.update(tab, history[reply.id]);
        M2M.utils.spinner_off(tab);
    };
}

function handle_script(data) {
    var elem = document.getElementById("script_result"),
        text = JSON.parse(data.text),
        contents = '';

    for (var i = 0; i < text.length; i++) {
        contents += text[i] + '\n'
    }
    elem.innerHTML = contents;
    M2M.utils.spinner_off("script");
}

function handle_schema(data) {
    var elem_schema = document.getElementById("schema_result_schema"),
        elem_keys   = document.getElementById("schema_result_keys"),
        reply, result_schema, result_keys;

    try {
        reply = JSON.parse(data.text);
        result_schema = M2M.utils.prettify(reply.schema);
        result_keys   = M2M.utils.prettify(reply.keys);
    } catch (e) {
        result = 'Error parsing JSON: ' + data + ', error: ' + e;
    }

    elem_schema.innerHTML = result_schema;
    elem_keys.innerHTML = result_keys;
    M2M.utils.spinner_off("schema");
}

function handle_write_file(data) {
    var elem_success,
        elem_result,
        date,
        message,
        contents;

    elem_success = document.getElementById("write_file_success");
    elem_result = document.getElementById("write_file_result");
    date = new Date();
    message = "Written file to ";
    contents = message + data.filename + '\n' + date.toLocaleTimeString() + ' - ' + date.toLocaleDateString();

    elem_success.innerHTML = 'Success';
    elem_result.innerHTML = contents;
    M2M.utils.spinner_off("write_file");
}

function handle_telemetry(data) {
    var elem_success,
        elem_result,
        date,
        message,
        contents;

    elem_success = document.getElementById("telemetry_success");
    elem_result = document.getElementById("telemetry_result");
    date = new Date();
    message = "Written file to ";
    contents = message + data.filename + '\n' + date.toLocaleTimeString() + ' - ' + date.toLocaleDateString();

    elem_success.innerHTML = 'Success';
    elem_result.innerHTML = contents;
    M2M.utils.spinner_off("telemetry");

    /*
     * The write_file spinner needs to be turned off because at the moment,
     * it is assumed that because the write_file JSON RPC method is used,
     * the tab must be the write file tab, so the write file spinner is
     * started instead of the telemetry one.
     */
    M2M.utils.spinner_off("write_file");
}

function handle_gpb(data) {
    M2M.build_proto_editor(JSON.parse(data.text).result);
    $('#proto_editor_wrapper').show();
    M2M.utils.spinner_off('gpb');
    // Necessary because the simple_cli JSON RPC request is used
    M2M.utils.spinner_off('simple_cli');
}

function handle_error(data) {
    var tab,
        elem_success,
        elem_result,
        error,
        traceback;
    
    tab = data.tab,
    elem_success = document.getElementById(tab + '_success'),
    elem_result  = document.getElementById(tab + '_result');
        
    error = data.error;
    traceback = data.traceback;

    elem_success.innerHTML = 'Error';
    elem_result.innerHTML = error + '/n /n' + traceback;
    M2M.utils.spinner_off(data.tab);
}

M2M.handler["request"]    = handle_request;
M2M.handler["get"]        = handle_reply("get");
M2M.handler["simple_cli"] = handle_reply("simple_cli");
M2M.handler["json_cli"]   = handle_reply("json_cli");
M2M.handler["protobuf"]   = handle_reply("protobuf");
M2M.handler["script"]     = handle_script;
M2M.handler["schema"]     = handle_schema;
M2M.handler["write_file"] = handle_write_file;
M2M.handler["telemetry"]  = handle_telemetry;
M2M.handler["gpb"]        = handle_gpb;
M2M.handler["error"]      = handle_error;

})(M2M, jQuery);
