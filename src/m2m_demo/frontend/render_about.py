# =============================================================================
# render_about.py
#
# This file implements the `About` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from m2m_demo.frontend import RegisterPage, BaseResource

class AboutTab(BaseResource):
    """
    About tab
    """
    def render_tab(self, request):
        self.has_debug_panel = False
        return help_html

help_html = '''\
<h1>About this app</h1>
<img src="about1.png" alt="about pic" class="about_pic"/>
<img src="about2.png" alt="about pic" class="about_pic"/>
<img src="about3.png" alt="about pic" class="about_pic"/>
'''

page = RegisterPage(AboutTab, tab="about")
