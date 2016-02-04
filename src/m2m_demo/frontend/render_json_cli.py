# =============================================================================
# render_json_cli.py
#
# This file implements the `JSON CLI` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json

from m2m_demo.frontend import RegisterPage, BaseResource
from m2m_demo.util.reformat import process_reply

class JsonCliTab(BaseResource):
    """
    JSON CLI tab
    """
    def render_tab(self, request):
        return html

    def render_POST(self, request):
        cmd = request.args['cmd'][0]
        fmt  = request.args['format'][0] # Requested data format
        d = request.sdata.api.cli_get(cmd)

        def got_reply(reply):
            text = process_reply(reply, fmt == 'nest')
            request.sdata.add_to_push_queue('json_cli', text=text)
            request.sdata.highlight('#json_cli_result')
            request.sdata.log('got reply id {}'.format(reply['id']))

        d.addCallback(got_reply)
        request.setHeader('Content-Type', 'application/json')
        return '{}'

html = '''\
<h1>JSON CLI</h1>
<form class="ajax_form" action="json_cli" method="post">
  <input name="cmd" id="json_cli_input" type="text" size="120" placeholder="Enter command here..." />
  <input type="submit" value="Go!" />
  <input type="radio" name="format" value="list" checked><span>List</span>
  <input type="radio" name="format" value="nest"><span>Nest</span>
</form>
<span class="spinner" id="spinner_json_cli"></span>
<hr />
<h3>Result: <span id="json_cli_success"></span></h3>
<pre id="json_cli_result"></pre>
'''

page = RegisterPage(JsonCliTab, path="/json_cli", tab="json_cli")
