# =============================================================================
# render_connection.py
#
# This file implements the `Connection` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import pickle

from twisted.internet import reactor
from m2m_demo.frontend import RegisterPage, BaseResource
from m2m_demo.api import ssh, json_rpc

DEFAULT_PATH = '/tmp/m2m-web-app-defaults'
try:
    DEFAULT_CONN_PARAMS = pickle.load(open(DEFAULT_PATH, 'rb'))
except Exception:
    DEFAULT_CONN_PARAMS = {
        'host': 'localhost',
        'username': 'cisco',
        'secret': '/src/assets/ssh/cisco_key',
        'secret_password': '',
        'secret_key': 'checked',
        'port': 22
    }

class ConnectionTab(BaseResource):
    """
    Connection tab
    """
    def render_tab(self, request):
        self.has_debug_panel = False
        cstate = request.sdata.connection_state
        # Send update for the initiate state, to let the javascript style everything
        reactor.callLater(0.1, lambda: request.sdata.set_conn_state(cstate))
        if hasattr(request.sdata, 'conn_params'):
            params = request.sdata.conn_params
        else:
            params = DEFAULT_CONN_PARAMS
        return connection_html.format(**params)

    def render_POST(self, request):
        if 'disconnect' in request.args:
            self._request_disconnection(request)
        else:
            # Save all the _inputdata, so it's the same next time
            conn_params = {x: request.args[x][0] for x in request.args.keys()}
            if request.args['secret_type'][0] == 'key':
                conn_params['secret_key'] = 'checked'
                conn_params['secret_password'] = ''
            else:
                conn_params['secret_key'] = ''
                conn_params['secret_password'] = 'checked'

            # Save both locally and across restarts
            request.sdata.conn_params = conn_params
            try:
                with open(DEFAULT_PATH, 'wb') as f:
                    pickle.dump(conn_params, f)
            except Exception as e:
                print('### failed to save defaults: ' + str(e))

            # Do the request
            self._request_connection(request)

    def _request_disconnection(self, request):
        request.sdata.transport_drop_cb()

    def _request_connection(self, request):
        cstate = request.sdata.connection_state
        if cstate != 'disconnected':
            # this shouldn't ever happen
            request.sdata.alert('Ignoring connection request mid-connection')
        else:
            request.sdata.log('starting connect with args {}'.format(request.args))
            if request.args['secret_type'][0] == 'key':
                key, password = request.args['secret'][0], None
            else:
                key, password = None, request.args['secret'][0]

            json_rpc.attach(request.sdata)
            ssh.connect(request.sdata, 'run json_rpc_server',
                        request.args['username'][0],
                        request.args['host'][0],
                        request.args['port'][0],
                        key, password)
        request.setHeader('Content-Type', 'application/json')
        return '{}'

connection_html = '''\
<h1>Router connection</h1>
<div class="status">
Connection status: <span id="connection_status"></span>
<img id="connection_loader" src="loader-red-circle.gif" alt="loading" />
<span id="connection_failure_reason"></span>
<button id="disconnect">Disconnect</button>
</div>
<form name="start_connection" id="start_connection" action="connection" method="post">
<fieldset id="connection_fieldset">
XR router address:
<input type="text" name="host" value="{host}" size="25">
<input type="submit" value="Connect">
<button id="toggle_creds">Credentials</button>
<div id="creds">
<span class="label">Username:</span>
<input type="text" name="username" value="{username}" size="30">
<span class="label">Secret:</span>
<input type="text" name="secret" value="{secret}" size="30">
<span class="label">Type:</span>
<input type="radio" name="secret_type" id="radio1" value="key" {secret_key}>
<label for="radio1">SSH key</label>
<input type="radio" name="secret_type" id="radio2" value="password" {secret_password}>
<label for="radio2">Password</label>
<span class="label">Port:</span>
<input type="text" name="port" value="{port}" size="10">
</div></fieldset></form>
<form class="ajax_form" action="yang_mode" id="yang_mode" method="post">
<input type="submit" value="Yang mode">
</form>
'''

page = RegisterPage(ConnectionTab, path="/connection", tab="connection")
