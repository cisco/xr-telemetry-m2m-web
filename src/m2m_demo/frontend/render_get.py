# =============================================================================
# render_get.py
#
# This file implements the `Get` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json

from m2m_demo.frontend import RegisterPage, BaseResource
from m2m_demo.util.reformat import process_reply

class GetTab(BaseResource):
    """
    Get tab
    """
    def render_tab(self, request):
        return html

    def render_POST(self, request):
        path = request.args['path'][0]   # Path to be queried
        fmt  = request.args['format'][0] # Requested data format
        d = request.sdata.api.get(path)

        def got_reply(reply):
            text = process_reply(reply, fmt == 'nest')
            request.sdata.add_to_push_queue('get', text=text)
            request.sdata.highlight('#get_result')
            request.sdata.log('got reply id {}'.format(reply['id']))

        d.addCallback(got_reply)
        request.setHeader('Content-Type', 'application/json')
        return '{}'

html = '''\
<h1>Get</h1>
<form class="ajax_form" action="get" method="post">
  <input type="text" name="path" id="get_input" size="120" placeholder="Enter path here..." />
  <input type="submit" value="Go!" />
  <input type="radio" name="format" value="list" checked><span>List</span>
  <input type="radio" name="format" value="nest"><span>Nest</span>
</form>
<span class="spinner" id="spinner_get"></span>
<hr />
<h3>Result: <span id="get_success"></span></h3>
<pre id="get_result"></pre>
'''

page = RegisterPage(GetTab, path="/get", tab="get")
