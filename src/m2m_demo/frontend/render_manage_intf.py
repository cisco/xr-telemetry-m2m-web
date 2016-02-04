# =============================================================================
# render_manage_intf.py
#
# This file implements the `Manage Interface` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json, re
from collections import OrderedDict
from twisted.internet.defer import inlineCallbacks
from m2m_demo.frontend import RegisterPage, BaseResource

class ManageIntfTab(BaseResource):
    """
    Manage interface tab - demonstrate config replace operations
    """
    def render_tab(self, request):
        return html

    def update_json(self, request):
        interface = request.args['interface'][0]
        base_path = "RootCfg.InterfaceConfiguration(" \
                    "['act', '{}'])".format(interface)

        cfg = OrderedDict()
        cfg[base_path + '.Description'] = request.args['description'][0]
        cfg[base_path + '.IPV4Network.Addresses.Primary'] = \
                OrderedDict((('Address', request.args['ipv4_addr'][0]),
                             ('Netmask', request.args['ipv4_mask'][0])))

            #[request.args['ipv4_addr'][0],
            # request.args['ipv4_mask'][0]]

        extra_cli = ["interface {} ".format(interface) + x
                     for x in request.args['extra_cli'][0].split('\n') if len(x) > 0]

        cfg_json = OrderedDict((('sets', cfg), ('cli_sets', extra_cli)))

        request.sdata.set_text('#manage_intf_json', json.dumps(cfg_json, indent=4))
        request.sdata.highlight('#manage_intf_json')
        return base_path, cfg, extra_cli

    def show_changes(self, request):
        base_path, json_dict, extra_cli = self.update_json(request)
        get_changes(json_dict, extra_cli, base_path, request.sdata)

    def commit(self, request):
        base_path, json_dict, extra_cli = self.update_json(request)
        do_commit(json_dict, extra_cli, request.sdata)

    def replace_subtree(self, request):
        base_path, json_dict, extra_cli = self.update_json(request)
        do_replace_subtree(json_dict, extra_cli, base_path, request.sdata)

    def replace_all(self, request):
        base_path, json_dict, extra_cli = self.update_json(request)
        do_replace_all(json_dict, extra_cli, base_path, request.sdata)

    def render_POST(self, request):
        action_map = {
            'Update JSON': self.update_json,
            'Show changes': self.show_changes,
            'Commit': self.commit,
            'Replace subtree': self.replace_subtree,
            'Replace all': self.replace_all
        }
        action_map[request.args['action'][0]](request)
        request.setHeader('Content-Type', 'application/json')
        return '{}'

@inlineCallbacks
def set_changes(json_dict, extra_cli, sdata):
    api = sdata.api
    for path, value in json_dict.items():
        yield api.set(path, value)
    for cli in extra_cli:
        yield api.cli_set(cli)

@inlineCallbacks
def get_changes(json_dict, extra_cli, base_path, sdata):
    api = sdata.api
    yield api.discard_changes()
    yield api.replace(base_path)
    yield set_changes(json_dict, extra_cli, sdata)
    changes = yield api.get_changes()
    display_result(changes, sdata)

@inlineCallbacks
def do_commit(json_dict, extra_cli, sdata):
    api = sdata.api
    yield api.discard_changes()
    yield set_changes(json_dict, extra_cli, sdata)
    result = yield api.commit(comment='M2M')
    display_result(result, sdata)

@inlineCallbacks
def do_replace_subtree(json_dict, extra_cli, base_path, sdata):
    api = sdata.api
    sdata.log('Doing replace for ' + base_path)
    yield api.discard_changes()
    yield api.replace(base_path)
    yield set_changes(json_dict, extra_cli, sdata)
    result = yield api.commit(comment='M2M')
    display_result(result, sdata)

@inlineCallbacks
def do_replace_all(json_dict, extra_cli, base_path, sdata):
    api = sdata.api
    sdata.log('Doing replace for ' + base_path)
    yield api.discard_changes()
    yield set_changes(json_dict, extra_cli, sdata)
    result = yield api.commit_replace(comment='M2M')
    display_result(result, sdata)

def display_result(result, sdata):
    # @@@@ some error handling would be nice
    res = result['result']
    if res is None:
        sdata.set_html('#manage_intf_success', 'No changes required')
    elif not isinstance(res, list):
        sdata.set_html('#manage_intf_success', 'Created new commit point ' + res)
    else:
        # @@@ for now convert double-quotes to single, even though it's invalid
        # @@@ JSON, to make it look nicer
        res = '<pre>' + json.dumps(res, indent=4) + '</pre>'
        res = re.sub(r'\\"', "'", res)
        sdata.set_html('#manage_intf_success', res)
        sdata.highlight('#manage_intf_success')
    sdata.add_to_push_queue('stop_current_spinner')

html = '''\
<h1>Manage Interface</h1>
<form class="ajax_form manage_intf" action="manage_intf" method="post">
<div id="manage_intf_json"></div>
<div>
<span class="label">Interface:</span>
<input type="text" name="interface" size="42" value="GigabitEthernet0/0/0/5" />
</div>
<div>
<span class="label">Description:</span>
<input type="text" name="description" size="42" value="to PHX" />
</div>
<div>
<span class="label">IPv4 address:</span>
<input type="text" name="ipv4_addr" size="15" value="10.5.128.6" />
mask:
<input type="text" name="ipv4_mask" size="15" value="255.255.255.252" />
</div>
<textarea name="extra_cli" rows="4" cols="43"
 placeholder="Additional config in CLI form"></textarea>
<div class="buttons">
<input type="submit" id="update_json_input" name="action" value="Update JSON">
<input type="submit" name="action" value="Show changes">
<input type="submit" name="action" value="Commit">
<input type="submit" name="action" value="Replace subtree">
<input type="submit" name="action" value="Replace all">
</div>
</form>
<span class="spinner" id="spinner_manage_intf"></span>
<hr />
<h3>Result:</h3>
<div id="manage_intf_success"></div>
'''

page = RegisterPage(ManageIntfTab, path="/manage_intf", tab="manage_intf")
