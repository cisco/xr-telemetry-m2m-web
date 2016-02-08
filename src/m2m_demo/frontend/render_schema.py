# =============================================================================
# render_schema.py
#
# This file implements the `Schema` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from m2m_demo.frontend import RegisterPage, BaseResource
from twisted.internet import defer
from json import dumps

def get_schema(api, path):
    return api.get_schema(path)

def get_keys(api, path):
    return api.get_children(path)

def extract_result(data):
    try:
        return data['result']
    except KeyError:
        return data['error']

class SchemaTab(BaseResource):
    """
    Schema tab
    """
    def render_tab(self, request):
        return html

    def render_POST(self, request):
        """
        Handle a request from the client.
        """
        path = request.args['path'][0]

        def send_response(data):
            response = {
                'schema': extract_result(data[0]),
                'keys':   extract_result(data[1])
            }
            request.sdata.add_to_push_queue('schema', text=dumps(response))
            request.sdata.highlight('#schema_result_schema')
            request.sdata.highlight('#schema_result_keys')
            request.sdata.log('got reply {}'.format(response))

        d_schema = get_schema(request.sdata.api, path)
        d_keys   = get_keys(request.sdata.api, path)

        # We only want to send a response once *both* JSON RPC requests have
        # been completed.
        d = defer.gatherResults([d_schema, d_keys])
        def canonicalize(results):
            # doesn't work @@@
            schema, keys = results
            if 'message' in keys and \
               'get_keys is not supported for leaf nodes' in keys['message']:
                keys = 'No keys (leaf node)'
            return (schema, keys)
        d.addCallback(canonicalize)
        d.addCallback(send_response)

        # For now, just send back an empty response.
        request.setHeader('Content-Type', 'application/json')
        return '{}'

html = '''\
<h1>Schema</h1>
<form class="ajax_form" action="schema" method="post">
  <input type="text" name="path" id="schema_input" size="120" placeholder="Enter path here..." />
  <input type="submit" value="Go!" />
</form>
<span class="spinner" id="spinner_schema"></span>
<hr />
<div>
<h3>Schema:</h3>
<pre id="schema_result_schema"></pre>
<h3>Keys:</h3>
<pre id="schema_result_keys"></pre>
</div>
'''

page = RegisterPage(SchemaTab, path="/schema", tab="schema")
