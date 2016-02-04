# =============================================================================
# render_protobuf.py
#
# This file implements the `Protocol Buffer` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json, re

from twisted.internet import defer

from m2m_demo.frontend import RegisterPage, BaseResource
from m2m_demo.util import scrape

class ProtobufTab(BaseResource):
    """
    Protobuf tab
    """
    def render_tab(self, request):
        return html

    def render_POST(self, request):
        #
        # Turn a path or show command into a set of candidate protobuf definitions.
        # If it looks like a show command, then schema-describe it, get the set of
        # paths, and run the GPB generation on each one. Otherwise, just run that on
        # the sole provided path.
        #
        path = request.args['path'][0].strip()
        if path.startswith('sh'):
            d = scrape.schema_describe(path, request.sdata)
        else:
            d = defer.succeed([path])
        
        def request_protobufs(paths):
            print('### PROTOBUF PATHS = {}'.format(paths))
            ds = []
            for path in reversed(paths):
                path = re.sub('\(.*?\)', '', path)
                ds.append(request.sdata.api.cli_exec(
                            'run telemetry_generate_gpb "{}"'.format(path)))
            return defer.DeferredList(ds)
        d.addCallback(request_protobufs)

        def get_protobufs(replies):
            line = '-' * 77
            sep = '\n//\n// ' + line + '\n//\n\n'
            text = sep.join([reply[1]['result'] for reply in replies])
            request.sdata.set_text('#protobuf_result', text)
            request.sdata.add_to_push_queue('stop_current_spinner')
            request.sdata.highlight('#protobuf_result')
        d.addCallback(get_protobufs)

        request.setHeader('Content-Type', 'application/json')
        return '{}'

html = '''\
<h1>Candidate Protocol Buffer definition</h1>
<form class="ajax_form" action="protobuf" method="post">
  <input type="text" name="path" size="120" placeholder="Enter path or show command here..." />
  <input type="submit" value="Go!" />
</form>
<span class="spinner" id="spinner_protobuf"></span>
<hr />
<h3>Result: <span id="protobuf_success"></span></h3>
<pre id="protobuf_result"></pre>
'''

page = RegisterPage(ProtobufTab, path="/protobuf", tab="protobuf")
