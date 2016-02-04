# =============================================================================
# config_map.py
#
# Create a mapping between CLI and JSON expressons of config.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

# @@@ The caching here ought to be done per-router (or router version or
# @@@ something) so this only works if all routers have the exact same
# @@@ XR version. Fix it.

import pickle, re
from exceptions import StopIteration

CACHE_PATH = '/tmp/m2m-web-app-map-cache'

class Map(object):

    def __init__(self, sh_run):
        self.sh_run = sh_run.split('\n')
        self.push_back = None
        self.index = 0
        self.cache_misses = []
        self.saved_cli_lines = []
        try:
            self.cache = pickle.load(open(CACHE_PATH, 'rb'))
            print('LOADED {} items from the MAP CACHE'.format(len(self.cache)))
        except Exception:
            self.cache = {}

    def next(self):
        index, self.index = self.index, self.index + 1
        return self.sh_run[index]

    def push_back(self):
        self.index -= 1

    def query(self, cli):
        if cli in self.cache:
            print "CACHE HIT: {} -> {}".format(cli, self.cache[cli])
            return self.cache[cli]
        else:
            print "CACHE MISS: {}".format(cli)
            self.cache_misses.append(cli)
            return "CACHE MISS"

    def populate_cache(self, map_data):
        for k, v in map_data:
            self.cache[k] = v
        try:
            with open(CACHE_PATH, 'wb') as f:
                    pickle.dump(self.cache, f)
        except Exception as e:
            print('### failed to save cache: ' + str(e))

    def map(self):
        for i in range(0, len(self.sh_run)):
            if not self.sh_run[i].startswith('!'):
                self.result = [(self.sh_run[0:i], '')]
                break

        self.walk_stanzas(i, 0, [])
        return self.result, self.cache_misses

    def walk_stanzas(self, index, indent, hierarchy_so_far):
        for i in range(index, len(self.sh_run)):
            if self.sh_run[i].startswith(' ' * (indent + 1)) or \
               self.sh_run[i] == ' ' * indent + '!':
               continue
            if indent > 0 and not self.sh_run[i].startswith(' ' * indent):
                break
            if indent == 0 and self.sh_run[i] == 'end':
                print 'FOUND END. i == {}, len() = {}'.format(i, len(self.sh_run))
                self.result.append(([self.sh_run[i]], ''))
                return
            self.map_stanza(i, indent, hierarchy_so_far)

    def map_stanza(self, index, indent, hierarchy_so_far):
        line = self.sh_run[index]
        hierarchy = hierarchy_so_far + [line.lstrip()]
        json_candidate = self.query(' '.join(hierarchy))
        self.saved_cli_lines.append(line)
        i = index + 1
        while re.match(' *(!|pass|end-policy)', self.sh_run[i]):
            self.saved_cli_lines.append(self.sh_run[i])
            i += 1
        if json_candidate is not None:
            self.result.append((self.saved_cli_lines, json_candidate))
            self.saved_cli_lines = []
        if index + 1 < len(self.sh_run) and \
           self.sh_run[index + 1].startswith(' ' * (indent + 1)):
            self.walk_stanzas(index + 1, indent + 1, hierarchy)

