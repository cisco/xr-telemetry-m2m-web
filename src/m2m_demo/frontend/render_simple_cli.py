# =============================================================================
# render_simple_cli.py
#
# This file implements the `Simple CLI` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from m2m_demo.frontend import RegisterPage, BaseResource
from json import dumps

class SimpleCliTab(BaseResource):
    """
    Simple CLI tab
    """
    def render_tab(self, request):
        return html

    def render_POST(self, request):
        cmd = request.args['cmd'][0]
        d = request.sdata.api.cli_exec(cmd)

        def got_reply(reply):
            request.sdata.add_to_push_queue('simple_cli', text=dumps(reply))
            request.sdata.log('got reply id {}'.format(reply['id']))

        d.addCallback(got_reply)
        request.setHeader('Content-Type', 'application/json')
        return '{}'

html = '''\
<h1>Simple CLI</h1>
<form class="ajax_form" action="simple_cli" method="post">
  <input type="text" name="cmd" id="simple_cli_input" size="120" placeholder="Enter command here..." />
  <input type="submit" value="Go!" />
</form>
<span class="spinner" id="spinner_simple_cli"></span>
<hr />
<h3>Result: <span id="simple_cli_success"></span></h3>
<pre id="simple_cli_result"></pre>
'''

page = RegisterPage(SimpleCliTab, path="/simple_cli", tab="simple_cli")
