# =============================================================================
# render_telemetry.py
#
# This file implements the `Telemetry Policy` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from m2m_demo.frontend import RegisterPage, BaseResource
from json import dumps
from m2m_demo.frontend.render_policies import get_policy_names
from twisted.internet.defer import inlineCallbacks

class TelemetryTab(BaseResource):
    """
    Telemetry tab
    """
    def render_tab(self, request):
        policy_html = ''
        for name in get_policy_names(self.cfg):
            policy_html +=  '<li><a href="#{0}">{0}</a></li>'.format(name)
        return html.format(policy_html)

    def render_POST(self, request):
        policy_filename = request.args['policy_name'][0]
        contents = request.args['policy'][0]
        full_filename = "/telemetry/policies/" + policy_filename

        def got_reply(reply):
            request.sdata.add_to_push_queue('telemetry',
                                            text=dumps(reply),
                                            filename=full_filename)
            request.sdata.log('got reply id {}'.format(reply['id']))
        def got_error(error):
            error_code = error.getErrorMessage()
            traceback = error.getTraceback()
            request.sdata.add_to_push_queue('error',
                                            error=error_code,
                                            traceback=traceback,
                                            tab='telemetry')

        d = request.sdata.api.write_file(full_filename, contents)
        d.addCallback(got_reply)
        d.addErrback(got_error)

        if('do_config' in request.args):
            self.config_telemetry(request)
        request.setHeader('Content-Type', 'application/json')
        return '{}'

    @inlineCallbacks
    def config_telemetry(self, request):
        # Set the telemetry config and commit
        api = request.sdata.api
        request.sdata.log('Configuring router for telemetry')

        # Gather required fields
        file_name = request.args['policy_name'][0]
        policy_name = file_name.split('.')[0]
        group = 'M2M_web'        # add to default group
        ip = request.args['destination_ip'][0]
        port = request.args['destination_port'][0]

        name_path = "RootCfg.Telemetry.JSON.PolicyGroup({'PolicyGroupName':"\
                    " '%s'}).Policy({'PolicyName': '%s'})" % (group, policy_name)
        dest_path = "RootCfg.Telemetry.JSON.PolicyGroup({'PolicyGroupName':"\
                    " '%s'}).IPv4Address({'IPAddr': '%s', 'TCPPort': %s})" % (group, ip, port)
        yield api.set(name_path, True)
        yield api.set(dest_path, True)
        yield api.commit(comment='telemetry')

html = '''\
<h1>Telemetry Policy</h1>
<div>
  <h4>Generate New Policy</h4>
  <div name="policy_builder" id="policy_builder">
    <span class="label">Policy name:</span>
    <input type="text" name="builder_name" id="builder_name" size="20" placeholder="my_policy">
    <br>
    <span class="label">Version:</span>
    <input type="text" name="builder_version" id="builder_version" size="5">
    <span class="label">Description:</span>
    <input type="text" name="builder_description" id="builder_description" size="50">
    <br>
    <span class="label">Comment:</span>
    <input type="text" name="builder_comment" id="builder_comment" size="30">
    <span class="label">Identifier:</span>
    <input type="text" name="builder_identifier" id="builder_identifier" size="30">
  </div>
  <button type="button" id="new_group" onclick="M2M.add_new_group_input()">Add group</button>
  <button type="button" id="builder_button" onclick="M2M.get_contents_from_builder()">Build policy file</button>
</div>
<br>
<hr />
<form class="ajax_form telemetry" action="telemetry" method="post">
  <h4>Policy To Be Written</h4>
  <div>
    <span class="label">Policy file name:</span>
    <input type="text" name="policy_name" id="telemetry_policy_name_box" size="30" placeholder="my_policy.policy">
  </div>
  <div>
    <textarea name="policy" id="telemetry_policy_contents" rows="6" onchange='M2M.fill_builder()' placeholder="Enter policy file here..."></textarea>
    <br>
    <span class="label">Add config?</span>
    <input type="checkbox" name="do_config" id="do_config" checked>
    <span class="label">Destination:</span>
    <input type="text" name="destination_ip" id="destination_ip" size="15">
    <span class="label">Port:</span>
    <input type="text" name="destination_port" id="destination_port" size="5">
    <input type="submit" value="Write to router" style="float: right;" />
  </div>
</form>
<div class="policy_loader">
  <h4>Load Example Policy</h4>
  <div class="preloaded_policies" name="preloaded_policies">
    <ul>{}</ul>
  </div>
  <h4>Upload Policy From File System</h4>
  <div>
    <input type='file' id='telemetry_policy_upload' onchange='M2M.get_contents_from_uploaded_policy()'>
  </div>
</div>
<span class="spinner" id="spinner_telemetry"></span>
<hr />
<h3>Result: <span id="telemetry_success"></span></h3>
<pre id="telemetry_result"></pre>
'''

page = RegisterPage(TelemetryTab, path="/telemetry", tab="telemetry")
