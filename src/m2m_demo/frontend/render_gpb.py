# =============================================================================
# render_gpb.py
#
# This file implements the `Telemetry GPB` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from m2m_demo.frontend import RegisterPage, BaseResource
from json import dumps

class GPBTab(BaseResource):
    """
    Telemetry GPB tab
    """
    def render_tab(self, request):
        return html

    def render_POST(self, request):
        path = request.args['gpb_path'][0]
        d = request.sdata.api.cli_exec("telemetry generate gpb-encoding path \"" + path + "\"")

        def got_reply(reply):
            request.sdata.add_to_push_queue('gpb', text=dumps(reply))
            request.sdata.log('got reply id {}'.format(reply['id']))

        d.addCallback(got_reply)
        request.setHeader('Content-Type', 'application/json')
        return '{}'


html = '''\
<h1>Telemetry GPB</h1>
<form class="ajax_form" id="gpb_form" action="gpb" method="post">
    <span class="label">Path:</span>
    <input type="text" id="gpb_path" name="gpb_path" size="50"/>
    <input type="button" id="gpb_path_button" value="Get Candidate File"/>
    <span class="spinner" id="spinner_gpb"></span>
</form>
<br><br>

<div id="proto_editor_wrapper">
    <hr>
    <h2>Edit Proto File</h2>
    <div id="proto_editor"></div>
</div>

<div id="gpb_result_wrapper">
    <hr />
    <h2>Generated file <span id="gpb_success"></span></h2>
    <pre id="gpb_result"></pre>
</div>
'''

page = RegisterPage(GPBTab, path="/gpb", tab="gpb")
