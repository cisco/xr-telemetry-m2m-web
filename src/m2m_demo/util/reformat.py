# =============================================================================
# reformat.py
#
# Reformat list-style [(path, value)] objects into nested-style 
# {path1: {path2: value}} objects
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json, re
from collections import OrderedDict

class OrderedDefaultDict(object):
    """
    Implements (most of) a default dict with ordering.
    """
    def __init__(self, factory):
        self._factory = factory
        self._dict = OrderedDict()

    def __setitem__(self, key, item):
        self._dict.__setitem__(key, item)

    def __getitem__(self, key):
        if key not in self._dict:
            self._dict[key] = self._factory()
        return self._dict.__getitem__(key)

    def __repr__(self):
        return self._dict.__repr__()

    def __iter__(self):
        return self._dict.__iter__()


def _recursive_default_dict():
    """
    Helper function to provide infinitely recursible default dicts.
    """
    return OrderedDefaultDict(_recursive_default_dict)

def _split(path):
    """
    Split a path into components, being aware that any named parameters
    in parentheses should always be left intact. eg:
    RootCfg.ISIS.Instance({'InstanceName': '1'}).NET({'NETName': '49.1921.6800.0004.00'})
    can't just be split on '.'.
    """
    in_arg = False
    last_idx = 0
    paths = []
    for idx, ch in enumerate(path):
        if in_arg:
            if ch == ')':
                in_arg = False
        else:
            if ch == '(':
                in_arg = True
            elif ch == '.':
                paths.append(path[last_idx:idx])
                last_idx = idx + 1
    paths.append(path[last_idx:idx + 1])
    return paths

def reformat(result):
    """
    Convert MPG-style data to a YFW-style nested structure.
    """
    root = _recursive_default_dict()

    for entry in result:
        path = entry[0]
        data = entry[1]
        parts = _split(path)

        # The final part of the path requires different handling from the bulk,
        # since this is the part whose value needs to be set to the data
        # corresponding to the whole path.
        bulk = parts[:-1]
        leaf = parts[-1]

        current = root
        for part in bulk:
            current = current[part]
        current[leaf] = data

    # @@@ ummm...
    root = eval(repr(root))

    return root

def process_reply(reply, nested=False):
    """
    Process a reply so it looks nice:

    - if it's from the prototype yang integration, ditch the 'data' root
    - convert from list to nested format if requested
    - convert quotes to avoid escaping
    """
    try:
        # @@@ strip 'data' from yang output
        reply['result'] = reply['result'][0]['data'] 
    except Exception:
        pass

    # If required, and query successful, convert the reply['result'] format.
    try:
        if nested:
            reply['result'] = reformat(reply['result'])
    except KeyError:
        # Fails silently if there is no 'reply['result']' in the reply['result'], this
        # means an error occurred.
        pass

    # @@@ cheesily try to avoid \" everywhere, at cost of valid json
    return re.sub(r'\\"', "'", json.dumps(reply))

