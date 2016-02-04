# =============================================================================
# render_script.py
#
# This file implements the `Script` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from __future__ import print_function
from collections import defaultdict, OrderedDict
from json import dumps
import sys, re, traceback
from twisted.internet import reactor, threads
from m2m_demo.frontend import RegisterPage, BaseResource
from m2m_demo.frontend.render_scriptlets import get_scriptlet_names
from m2m_demo.util.types import m2mstr_object_hook


def api_method(request, method):
    """
    Utility function to create a synchronous wrapper for the JSON-RPC API.
    """
    def method_fn(*args, **kwargs):
        fn = getattr(request.sdata.api, method)
        res = threads.blockingCallFromThread(reactor, fn, *args, **kwargs)
        try:
            ret = res['result']
            ret = m2mstr_object_hook(ret)
        except KeyError:
            ret = res['error']
        return ret

    return method_fn

class ScriptTab(BaseResource):
    """
    Python script tab
    """
    def render_tab(self, request):
        scriptlet_html = ''
        for name in get_scriptlet_names(self.cfg):
            scriptlet_html +=  '<li><a href="#{0}">{0}</a></li>'.format(name)
        return html.format(scriptlet_html)

    def render_POST(self, request):
        """
        Handle a request from the client.
        """
        script_env = {
            method: api_method(request, method)
            for method in request.sdata.api.fns
        }

        # Make get do auto-formatting for convenience, even though this
        # breaks if you try to use literal '{}' named arguments
        # @@@ reconsider whether this is at all a good idea
        def get_with_formatting(path, *args):
            return api_method(request, 'get')(path.format(*args))
        script_env['get'] = get_with_formatting

        script_env['re'] = re
        script_env['dumps'] = dumps
        script_env['defaultdict'] = defaultdict
        script_env['OrderedDict'] = OrderedDict

        buf = []
        def dummy_print(*args):
            if len(args) == 1 and (isinstance(args[0], list) or isinstance(args[0], dict)):
                buf.append(dumps(args[0], indent=4))
            else:
                buf.append(' '.join(map(str, args)))
        script_env['print'] = dummy_print

        def run_script(script):
            try:
                exec script in script_env
            except:
                exception_info = sys.exc_info()
                buf.extend(traceback.format_exception(*exception_info))
            request.sdata.log('got reply {}'.format(buf))
            request.sdata.add_to_push_queue('script', text=dumps(buf))

        script = request.args['script'][0]
        reactor.callInThread(run_script, script)


html = '''\
<h1>Run script</h1>
<form id="script_form" class="ajax_form" action="script" method="post">
  <textarea form="script_form" name="script" id="script_box" rows="10" cols="120" placeholder="Enter script here..."></textarea>
  <input type="submit" value="Go!" />
</form>
<div class="script_loader">
Examples
<ul>{}</ul>
</div>
<span class="spinner" id="spinner_script"></span>
<hr />
<h3>Result: <span id="script_success"></span></h3>
<pre id="script_result"></pre>
'''

page = RegisterPage(ScriptTab, path="/script", tab="script")
