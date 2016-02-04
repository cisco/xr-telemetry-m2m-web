# =============================================================================
# render_policies.py
#
# This file handles serving the telemetry policy files.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json, os, re
from collections import OrderedDict

from m2m_demo.frontend import RegisterPage, BaseResource

policies = OrderedDict()

def get_policy_names(cfg):
    maybe_load_policies(cfg, policies)
    return policies.keys()

def get_policy_contents(cfg, filename):
    return policies[filename]

def maybe_load_policies(cfg, policies_dict):
    # Update policies_dict with files found in /src/assets/policies
    policy_dir = os.path.join(cfg['assets'], 'policies')
    for root, dirs, files in os.walk(policy_dir):
        for filename in files:
            contents = open(os.path.join(root, filename)).read()
            policies_dict[filename] = contents
    return policies_dict

class PoliciesPage(BaseResource):
    """
    Serve up policies as a json object
    """
    def render_GET(self, request):
        request.setHeader('Content-Type', 'application/json')
        temp_pols = maybe_load_policies(self.cfg, policies)

        global policies
        policies = temp_pols
        return json.dumps(policies)

page = RegisterPage(PoliciesPage, '/policies')
