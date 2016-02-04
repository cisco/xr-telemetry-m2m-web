# =============================================================================
# render_home.py
#
# This file implements the `Home` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import os

from m2m_demo.frontend import RegisterPage, BaseResource

class HomePage(BaseResource):
    """
    Home page. This is bolted together from a big static head fetched from
    a file, dynamic contributions from each plugin with a tab, and a static tail.
    """
    def __init__(self, cfg):
        BaseResource.__init__(self, cfg)
        index_html_path = os.path.join(self.cfg['assets'], 'fragments/index.html')
        with open(index_html_path) as f:
            self.index_html_base = f.read()

    def render_GET(self, request):
        parts = [self.index_html_base]
        for tab, resource in self.cfg['tab_map'].items():
            parts.append('<div class="tab" id="{}">'.format(tab))
            tab_plugin = resource(self.cfg)
            parts.append(tab_plugin.render_tab(request))
            if tab_plugin.has_debug_panel:
                parts.append('<div class="debug" id="{}_debug"><table></table></div>'.
                             format(tab))
            parts.append('</div>')
        parts.append('</div></div></body></html>')
        return '\n'.join(parts)

page = RegisterPage(HomePage, '/')
