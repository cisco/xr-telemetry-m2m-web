# =============================================================================
# __init__.py
#
# Frontend plumbing. This is a bunch of twisted glue that means we can write
# standalone render_*.py modules, that each declare where they plug into the
# URL path, and the dispatch then does the right thing.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from zope.interface import Interface, implements
from twisted.plugin import IPlugin, getPlugins
from twisted.web.resource import Resource
import m2m_demo

class IWebResource(Interface):
    """
    Custom Twisted plugin specification for a web page renderer
    """
    def register(self, path_map, tab_map):
        """
        Register a resource with the site
        """

class RegisterPage(object):
    """
    Custom Twisted plugin for registering a web page renderer
    """
    implements(IPlugin, IWebResource)

    def __init__(self, resource, path=None, tab=None):
        """
        Remember any path and tab mappings for this renderer.
        """
        self.resource = resource
        self.path = path
        self.tab = tab

    def register(self, path_map, tab_map):
        """
        Actually register a mapping of path to resource.
        The child_path_map is used to register URLs.
        The child_tab_map is used to register tabs on the main page.
        """
        if self.path:
            path_map[self.path] = self.resource
        if self.tab:
            tab_map[self.tab] = self.resource

class BaseResource(Resource):
    """
    Base class for discovered web resources
    """
    isLeaf = True

    def __init__(self, cfg):
        Resource.__init__(self)
        self.cfg = cfg
        self.has_debug_panel = True

def discover_resources():
    """
    Find all plugin resources and return the details of both paths and tabs.
    """
    path_map = {}
    tab_map = {}
    for plugin in getPlugins(IWebResource, m2m_demo.frontend):
        plugin.register(path_map, tab_map)
    return path_map, tab_map
