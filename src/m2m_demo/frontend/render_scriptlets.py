# =============================================================================
# render_scriptlets.py
#
# This file handles serving the sample scripts.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json, os, re
from collections import OrderedDict

from m2m_demo.frontend import RegisterPage, BaseResource

scriptlets = None

def get_scriptlet_names(cfg):
    maybe_load_scriptlets(cfg)
    return scriptlets.keys()

def maybe_load_scriptlets(cfg):
    if scriptlets is not None:
        return
    global scriptlets
    scriptlets = OrderedDict()
    scriptlet_dir = os.path.join(cfg['assets'], 'scriptlets')
    for root, dirs, files in os.walk(scriptlet_dir):
        for filename in files:
            contents = open(os.path.join(root, filename)).read()
            m = re.search('_(.*)\.py', filename)
            if m:
                filename = m.group(1)
            scriptlets[filename] = contents

class ScriptletsPage(BaseResource):
    """
    Serve up scriptlets as a json object
    """
    def render_GET(self, request):
        request.setHeader('Content-Type', 'application/json')
        maybe_load_scriptlets(self.cfg)
        return json.dumps(scriptlets)

page = RegisterPage(ScriptletsPage, '/scriptlets')
