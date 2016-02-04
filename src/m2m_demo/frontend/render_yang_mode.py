# =============================================================================
# render_yang_mode.py
#
# This file implements the Yang mode callback.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from m2m_demo.frontend import RegisterPage, BaseResource

class YangModeCallback(BaseResource):
    def render_POST(self, request):
        print('### starting yfw mode')
        request.sdata.api.yfw()
        request.setHeader('Content-Type', 'application/json')
        return '{}'

page = RegisterPage(YangModeCallback, path="/yang_mode")
