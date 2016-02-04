# =============================================================================
# render_explorer.py
#
# This file implements the `Explorer` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from m2m_demo.frontend import RegisterPage, BaseResource
from json import loads, dumps
from twisted.internet import defer

class ExplorerTab(BaseResource):
    """
    Experimental explorer tab
    """
    def render_tab(self, request):
        return html

    def render_POST(self, request):
        paths = request.args['paths[]']

        def got_data(responses):
            reply = {}
            for path, data in zip(paths, responses):
                try:
                    reply[path] = data['result']
                except KeyError:
                    reply[path] = data['error']
            request.sdata.add_to_push_queue('explorer', text=dumps(reply))
            request.sdata.log('got reply {}'.format(paths))

        reqs = map(request.sdata.api.get_schema, paths)
        d = defer.gatherResults(reqs)
        d.addCallback(got_data)

        request.setHeader('Content-Type', 'application/json')
        return '{}'

html = '''\
<h1 id="explorer_title" style="display: table-cell; width: 300px">Schema Explorer</h1>
<div id="explorer_show_hide" style="display: table-cell; transform: translateY(-10%);">
  <button id="explorer_show_hide_button" type="button">Show</button>
</div>
<div id="explorer_body">
    <div id="explorer_form_explanation">
      When you click on a path below, it will fill in the most recently clicked on or created path box.
    </div>
    <span class="spinner" id="spinner_explorer"></span>
    <div id="explorer_wrapper" style="height: ; overflow: auto;"> <!-- style is to make scrollable in telemetry tab -->
      <pre id="explorer_display"></pre>
      <div id="explorer_root"></div>
    </div>
</div>
'''

page = RegisterPage(ExplorerTab, path="/explorer", tab="explorer")
