# =============================================================================
# render_write_file.py
#
# This file implements the `Write File` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from m2m_demo.frontend import RegisterPage, BaseResource
from json import dumps
from m2m_demo.frontend.render_policies import get_policy_names


class WriteFileTab(BaseResource):
    """
    Write File tab
    """
    def render_tab(self, request):
        file_html = ''
        for name in get_policy_names(self.cfg):
            file_html +=  '<li><a href="#{0}">/src/assets/policies/{0}</a></li>'.format(name)
        return html.format(file_html)

    def render_POST(self, request):
        file_path = request.args['file_path'][0]
        data = request.args['file_contents'][0]

        def got_reply(reply):
            request.sdata.add_to_push_queue('write_file',
                                            text=dumps(reply),
                                            filename=file_path)
            request.sdata.log('got reply id {}'.format(reply['id']))

        def got_error(error):
            error_code = error.getErrorMessage()
            traceback = error.getTraceback()
            request.sdata.add_to_push_queue('error',
                                            error=error_code,
                                            traceback=traceback,
                                            tab='write_file')

        d = request.sdata.api.write_file(file_path, data)
        d.addCallback(got_reply)
        d.addErrback(got_error)
         
        request.setHeader('Content-Type', 'application/json')
        return '{}'

html = '''\
<h1>Write File</h1>
<form class="ajax_form write_file" action="write_file" method="post">
  <div>
    <span class="label">Destination path:</span>
    <input type="text" name="file_path" id="file_path_box" size="30" placeholder="Full destination path here...">
  </div>
  <div>
    <textarea name="file_contents" id="file_contents" rows="10" cols="120" placeholder="Enter text here..."></textarea>
    <input type="submit" value="Write to router" />
  </div>
</form>
<div class="file_loader">
<div class="preloaded_files" name="preloaded_files">
Examples
<ul>{}</ul>
</div>
<div>
<input type="file" id="file_upload" onchange="M2M.get_contents_from_uploaded_file()">
</div>
</div>
<span class="spinner" id="spinner_write_file"></span>
<hr />
<h3>Result: <span id="write_file_success"></span></h3>
<pre id="write_file_result"></pre>
'''

page = RegisterPage(WriteFileTab, path="/write_file", tab="write_file")
