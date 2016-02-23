# =============================================================================
# json_rpc.py
#
# This file implements the JSON-RPC frontent.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json
from collections import OrderedDict
from twisted.internet import defer

def attach(sdata):
    """
    Create a JSON-RPC object and attach to the session
    """
    JsonRpc(sdata)

class JsonRpcException(Exception):
    pass

api_fns = {}

class JsonRpc(object):
    """
    Object that understands the JSON-RPC protocol
    """

    # Decorator to build up a dict containing all of the API functions for
    # convenient access by user-defined scripts.
    def api_fn(fn):
        api_fns[fn.__name__] = fn
        return fn

    #
    # The public API of the remote server, all return a 'deferred'.
    #

    # Version Inspection

    @api_fn
    def get_version(self):
        return self._request("get_version")

    # Access Operations

    @api_fn
    def get(self, path):
        return self._request("get", path=path)

    @api_fn
    def get_children(self, path):
        return self._request("get_children", path=path)

    @api_fn
    def get_parent(self, path):
        return self._request("get_parent", path=path)

    @api_fn
    def set(self, path, value):
        return self._request("set", path=path, value=value)

    @api_fn
    def delete(self, path):
        return self._request("delete", path=path)

    @api_fn
    def replace(self, path):
        return self._request("replace", path=path)

    # Config Operations

    @api_fn
    def commit(self, label="", comment=""):
        return self._request("commit", label=label, comment=comment)

    @api_fn
    def commit_replace(self, label="", comment=""):
        return self._request("commit_replace", label=label, comment=comment)

    @api_fn
    def discard_changes(self):
        return self._request("discard_changes")

    @api_fn
    def get_changes(self):
        return self._request("get_changes")

    # Schema inspection

    @api_fn
    def get_schema(self, path, fields=None):
        if fields is None:
            return self._request("get_schema", path=path)
        else:
            return self._request("get_schema", path=path, fields=fields)

    # CLI Execution

    @api_fn
    def cli_exec(self, command):
        return self._request("cli_exec", command=command)

    @api_fn
    def cli_get(self, command):
        return self._request("cli_get", command=command)

    @api_fn
    def cli_set(self, command):
        return self._request("cli_set", command=command)

    @api_fn
    def cli_describe(self, command, configuration):
        return self._request("cli_describe",
                             command=command,
                             configuration=configuration)

    # File Management Operations

    @api_fn
    def write_file(self, filename, data):
        return self._request("write_file", filename=filename, data=data)

    # Utility Operations

    @api_fn
    def normalize_path(self, path):
        return self._request("normalize_path", path=path)

    # YFW mode hack
    def yfw(self):
        return self._request("yfw")

    ######################################################################

    #
    # Internals
    #

    def __init__(self, sdata):
        self.sdata = sdata
        sdata.api = self
        sdata.transport_rx_cb = self._reply
        sdata.transport_dropped_cb = self._connection_dropped
        self.next_id = 1
        self.pending_reply_map = {}
        self.fns = api_fns

    def _request(self, method, **params):
        """
        Send a request over whatever transport is provided
        """
        this_id = self.next_id
        self.next_id += 1
        request = r'{{"jsonrpc": "2.0", "id": {}, "method": "{}", "params": {}}}' \
                    .format(this_id, method, json.dumps(params))
        print('### SENDING REQUEST {}'.format(request))
        self.sdata.add_to_push_queue('request', text=request)
        self.sdata.transport_tx_cb(request)
        d = defer.Deferred()
        self.pending_reply_map[this_id] = d
        return d

    def _reply(self, json_reply):
        """
        Handle a reply that came in over the transport provided
        """
        if not json_reply.startswith('{'):
            self.sdata.log('Received non-JSON data: "{}"'.format(json_reply))
            return
        reply = json.loads(json_reply, object_pairs_hook=OrderedDict)
        if reply['jsonrpc'] != '2.0' or 'id' not in reply or reply['id'] is None:
            self.sdata.log('Received bad JSON-RPC reply: {}'.format(json_reply))
            if len(self.pending_reply_map) == 1:
                # lucky! can guess a pending reply to kill
                this_id = self.pending_reply_map.keys()[0]
                d = self.pending_reply_map[this_id]
                del self.pending_reply_map[this_id]
                e = JsonRpcException('Bad reply: {}'.format(json_reply))
                d.errback(e)
            return
        this_id = int(reply['id'])
        if 'method' in reply and this_id in self.pending_reply_map:
            self.sdata.log('Got echo of request for {}, ignoring'.format(this_id))
        else:
            d = self.pending_reply_map[this_id]
            del self.pending_reply_map[this_id]
            d.callback(reply)

    def _connection_dropped(self):
        """
        Handle the connection dropping
        """
        for this_id, d in self.pending_reply_map.items():
            self.sdata.log("Killing deferred for {}".format(this_id))
            d.errback()
        self.pending_reply_map = {}
