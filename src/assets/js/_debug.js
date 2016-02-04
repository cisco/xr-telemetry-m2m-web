/*
 * ============================================================================
 * _debug.js
 *
 * This file implements the debug infrastructure.
 *
 * December 2015
 *
 * Copyright (c) 2015 by cisco Systems, Inc.
 * All rights reserved.
 * ============================================================================
 */

var M2M = M2M || {};
(function (M2M) {

function update_debug(tab, entry) {
    var elem = document.getElementById(tab + '_debug')
                       .getElementsByTagName('table')[0],
        row1 = document.createElement('tr'),
        row2 = document.createElement('tr'),
        req = document.createElement('td'),
        rep = document.createElement('td');

    req.innerHTML = entry.request;
    rep.innerHTML = entry.reply;

    req.className = 'json_request';
    rep.className = 'json_reply';

    row1.appendChild(document.createElement('td'));
    row1.appendChild(document.createElement('td'));
    row1.appendChild(req);

    row2.appendChild(rep);
    row2.appendChild(document.createElement('td'));
    row2.appendChild(document.createElement('td'));
    elem.insertBefore(row2, elem.childNodes[0]);
    elem.insertBefore(row1, elem.childNodes[0]);
}

M2M.debug = {
    "update": update_debug
};

})(M2M);
