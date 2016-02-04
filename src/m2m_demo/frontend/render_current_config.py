# =============================================================================
# render_current_config.py
#
# This file implements the `Current Config` tab.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json, re

from m2m_demo.frontend import RegisterPage, BaseResource
from m2m_demo.util import config_map, scrape


def progress_indicator(request, progress):
    """Tell the client about config mapping progress."""
    request.sdata.add_to_push_queue('current_cfg_progress',
                                    progress=progress)


class CurrentConfigTab(BaseResource):
    """
    Current config tab
    """
    def render_tab(self, request):
        return html

    def render_POST(self, request):
        self.attempt_map(request)
        request.setHeader('Content-Type', 'application/json')
        return '{}'

    def attempt_map(self, request, second_attempt=False):
        if not second_attempt:
            progress_indicator(request, "Determining current config...")
        d = request.sdata.api.cli_exec('show running')

        def got_reply(reply):
            if not second_attempt:
                progress_indicator(request, "Checking cached mappings...")
            print '### reply[result] = {}'.format(reply['result'])
            mapper = config_map.Map(reply['result'])
            map_result, map_misses = mapper.map()
            if len(map_misses) == 0:
                progress_indicator(request, "Generating HTML response...")
                d = request.sdata.api.get('RootCfg')
                def got_root_cfg(root_cfg):
                    html = self.format_table(map_result, root_cfg['result'])
                    request.sdata.add_to_push_queue('set_html',
                                                    selector='#current_config_result',
                                                    html=html)
                    progress_indicator(request, "Mapping complete")
                    request.sdata.add_to_push_queue('current_cfg_loaded')
                    request.sdata.add_to_push_queue('stop_current_spinner')
                d.addCallback(got_root_cfg)
                # @@@ missing error handling
            elif second_attempt:
                print 'STILL MISSES ON SECOND ATTEMPT'
                request.sdata.add_to_push_queue('set_text',
                                                selector='#current_config_result',
                                                text=json.dumps(map_misses, indent=4))
                request.sdata.add_to_push_queue('stop_current_spinner')
            else:
                progress_indicator(request, "Some mappings not available from cache, searching...")
                self.handle_misses(request, mapper, map_misses)

        d.addCallback(got_reply)
        return d

    def handle_misses(self, request, mapper, map_misses):
        self.num_misses = len(map_misses)
        self.found_values = []
        for i, miss in enumerate(map_misses):
            progress_indicator(
                request,
                "Incomplete mapping from cache, calculating remainder [{}/{}]..."
                    .format(i + 1, self.num_misses))
            print('### FETCHING MISS {}/{}: {}'.format(i, self.num_misses, miss))
            d = scrape.schema_describe('config ' + miss, request.sdata)
            def got_miss_reply(result, key):
                result = [re.sub("'", '"', path) for path in result]
                if len(result) == 0:
                    result = None
                print('### GOT RESULT ({} remaining, {} saved) {} -> {}'.format(
                        self.num_misses, len(self.found_values), key, result))
                self.found_values.append((key, result))
                self.num_misses -= 1
                if self.num_misses == 0:
                    # Got everything!
                    mapper.populate_cache(self.found_values)
                    self.attempt_map(request, second_attempt=True)
            d.addCallback(got_miss_reply, miss)

    def format_table(self, data, root_cfg):
        output = ['<table>']
        first_row = True
        seen = set()
        cfg = dict(root_cfg)
        from pprint import pprint
        pprint(cfg)
        for cli, json_paths in data:
            cli_td = '\n'.join(cli)
            json_to_show = []
            info_paths = []
            for path in json_paths:
                if path in seen:
                    info_paths.append(path)
                else:
                    json_to_show.append(path)
                    if path not in cfg:
                        print("### Missing path {}".format(path))
                    # @@@ confused by the error option below - set to something
                    # @@@ visible to debug
                    json_to_show.append('<span class="value">' + \
                                        json.dumps(cfg.get(path, ""), indent=4) +
                                        '</span>')
                    seen.add(path)
            json_td = '\n'.join(json_to_show)

            if first_row:
                output.append('<tr><td colspan="3" class="cli">{}</td></tr>'.format(cli_td))
                first_row = False
            else:
                if len(info_paths):
                    text = "Requires parent: " + '\n'.join(info_paths)
                    info_td = '''<img class="info" src="info.png" title='{}' alt="" />'''.format(text)
                else:
                    info_td = ''
                output.append('<tr><td class="cli">{}</td>' \
                              '<td class="path">{}</td>'
                              '<td class="path">{}</td></tr>'. \
                              format(cli_td, info_td, json_td))
        output.append('</table>')
        return '\n'.join(output)


html = '''\
<h1>Current configuration</h1>
<div class="toggle_cli_or_json">
  Show/hide:
  <br><input type="checkbox" name="toggle_cli" checked>CLI
  <br><input type="checkbox" name="toggle_path" checked>JSON paths
  <br><input type="checkbox" name="toggle_value" checked>JSON values
</div>
<form class="ajax_form" action="current_config" method="post">
  <input type="submit" value="Update" />
  <span class="spinner" id="spinner_current_config"></span>
  <span id="current_config_progress"></span>
</form>
<div id="current_config_result"></div>
'''

page = RegisterPage(CurrentConfigTab, path="/current_config", tab="current_config")
