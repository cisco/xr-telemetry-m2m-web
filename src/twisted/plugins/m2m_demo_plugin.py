# =============================================================================
# m2m_demo_plugin.py
#
# This file implements the M2M demo twisted plugin.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application import internet, service

from m2m_demo.frontend import web

class Options(usage.Options):
    pass

#
# Built-in configuration/defaults.
#
web_cfg = {
    'assets': './assets',
    'http_port': '8080',
}

class M2MDemoServiceMaker(object):

    implements(service.IServiceMaker, IPlugin)

    tapname = "m2m_demo"
    description = "Web M2M demo client"
    options = Options

    def makeService(self, options):
        top_service = service.MultiService()

        # Start the web server
        web_service = web.start(web_cfg)
        tcp_service = internet.TCPServer(int(web_cfg['http_port']), web_service)
        tcp_service.setServiceParent(top_service)

        return top_service

service_maker = M2MDemoServiceMaker()
