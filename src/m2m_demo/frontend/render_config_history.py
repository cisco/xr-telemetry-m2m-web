# =============================================================================
# render_config_history.py
#
# This file implements the `Config History` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

from twisted.web import server
from twisted.internet import reactor

from m2m_demo.frontend import RegisterPage, BaseResource
from m2m_demo.util import scrape

# @@@ broken! needs to change to per-router
commit_cache = {}

class ConfigHistoryPage(BaseResource):
    '''
    Page that shows the config history
    '''
    def render_tab(self, request):
        return tab_html

    def render_POST(self, request):
        if 'fetch_id' in request.args:
            return self.render_single_diff(request, request.args['fetch_id'][0])
        else:
            return self.render_history(request)

    def render_single_diff(self, request, fetch_id):
        def dispatch_diff():
            request.sdata.add_to_push_queue('set_text',
                                            selector='#cfg_diff_' + fetch_id,
                                            text=commit_cache[fetch_id])
        def done(result_cli):
            global commit_cache
            commit_cache[fetch_id] = result_cli['result']
            dispatch_diff()
        if fetch_id in commit_cache:
            print "### COMMIT CACHE HIT"
            dispatch_diff()
        else:
            d = request.sdata.api.cli_exec('show configuration commit changes '+ fetch_id)
            d.addCallback(done)

    def render_history(self, request):
        last_id = request.args.get('last_id', [2000000000])[0]
        main_headings = ('Time', 'Commit ID', 'Comment')
        sub_headings = ('Label', 'User', 'Line', 'Client')
        thead = '<table class="history"><tr><th>&nbsp;</th>' + \
                ''.join(['<th>{}</th>'.format(h) for h in main_headings]) + \
                '</tr>'

        def done(result_cli):
            result = scrape.commit_history(result_cli['result'])
            table = ''
            commit_ids = []
            for entry in result:
                commit_id = entry['Commit ID']
                if int(commit_id) > int(last_id):
                    row_style = 'class="new"'
                else:
                    row_style = ""
                row = '<tr {}><td><button id="toggle_{}">X</button></td>'.format(row_style, commit_id)
                for h in main_headings:
                    row += '<td>{}</td>'.format(entry[h])
                table += row + '</tr>\n'
                row = '<tr class="subrow" id="subrow_{}"><td colspan=4></a>'.format(commit_id)
                for h in sub_headings:
                    if entry[h] != "":
                        row += '<span><b>{}:</b> {}</span>'.format(h, entry[h])
                table += row + '<pre id="cfg_diff_{}"></pre></td></tr>\n'.format(commit_id)
                commit_ids.append(entry['Commit ID'])
            html = thead + table + '</div>'
            request.sdata.add_to_push_queue('set_html',
                                            selector='#cfg_hist_output',
                                            html=html)
            request.sdata.add_to_push_queue('commit_history_updates')
            for commit_id in commit_ids:
                self.render_single_diff(request, commit_id)
        d = request.sdata.api.cli_exec('show configuration history commit reverse detail')
        d.addCallback(done)
        return '{}'

tab_html = '''\
<h1>Configuration commit history</h1>
    <form class="ajax_form" action="history" method="post">
    <input type="submit" value="Update" /></form>
<div id="cfg_hist_output"></div>
'''

page = RegisterPage(ConfigHistoryPage, path='/history', tab='history')
