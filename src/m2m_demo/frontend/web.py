# =============================================================================
# m2m_demo_plugin.py
#
# Set up the web service.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import os, re
from twisted.web.resource import Resource, NoResource
from twisted.web.static import File
from twisted.web.server import Site
from m2m_demo.frontend import discover_resources, session


class Root(Resource):
    """
    This manages the overall routing of requests for the site
    """
    def __init__(self, cfg, static):
        Resource.__init__(self)
        self.cfg = cfg
        self.static = static
        self.path_map, self.tab_map = discover_resources()

    def getChild(self, name, request):
        """
        Dispatch a specific incoming request to an appropriate resource
        """
        # First try: static resource
        static = self.static.handle_static(request)
        if static:
            return static

        # If that doesn't serve the request, try the plugin dynamic path
        if request.path in self.path_map:
            print 'using plugin %s for %s' % (self.path_map[request.path], request.path)
            cfg = self.cfg.copy()
            cfg['tab_map'] = self.tab_map
            for arg in request.args:
                if arg not in cfg:
                    cfg[arg] = request.args[arg][0]
            # Augment the request with our own session data
            request.sdata = session.get_data(request)
            return self.path_map[request.path](cfg)

        # Nothing else to try
        print 'Failed to match path', request.path, 'to any plugins', self.path_map
        return NoResource()

class Static(object):
    """
    Serve up static assets
    """
    def __init__(self, cfg):
        static_dir = os.path.join(cfg['assets'], 'static')
        self.files = {}
        for root, dirs, files in os.walk(static_dir):
            for filename in files:
                if not filename.startswith('!'):
                    fullpath = os.path.join(root, filename)
                    self.files[filename] = File(fullpath)

    def handle_static(self, request):
        r = re.search(r'.*/(.+)', request.path)
        if r and r.group(1) in self.files:
            return self.files[r.group(1)]
        return None

def start(web_cfg):
    """
    Start the web service
    """
    static = Static(web_cfg)
    root_resource = Root(web_cfg, static)
    site = Site(root_resource)
    return site

