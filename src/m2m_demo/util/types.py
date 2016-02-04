# =============================================================================
# types.py
#
# Handy types to make scriptlets more concise.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import json, re
from collections import OrderedDict

class M2MString(str):

    def __getitem__(self, name):
        """
        Return a naming element from a path
        """
        d = self._dict()
        if isinstance(name, int):
            return d.values()[name]
        else:
            return d[name]

    def _dict(self):
        """
        Construct an ordered dict from the naming elements of the path
        """
        d = OrderedDict()
        for json_fragment in re.findall('\((.*?)\)', self, re.M):
            json_ordered_dict = json.loads(re.sub("'", '"', json_fragment), 
                                           object_pairs_hook=OrderedDict)
            d.update(json_ordered_dict)
        return d

class M2MList(list):

    def __getattr__(self, name):
        if name == 'val':
            return self._val()
        else:
            return list(self).__getattr__(name)

    def _val(self):
        """
        Consider list as a val and try to be helpful
        """
        v = self
        if len(v) == 1:
            v = v[0]
        if len(v) == 2:
            v = v[1]
        return v


def m2mstr_object_hook(val_in):
    if isinstance(val_in, str) or isinstance(val_in, unicode):
        return M2MString(val_in)
    elif isinstance(val_in, dict):
        return m2mstr_object_hook_dict(val_in)
    elif isinstance(val_in, list):
        return m2mstr_object_hook_list(val_in)
    else:
        return val_in

def m2mstr_object_hook_dict(dict_in):
    dict_out = OrderedDict()
    for k, v in dict_in.items():
        k = m2mstr_object_hook(k)
        v = m2mstr_object_hook(v)
        dict_out[k] = v
    return dict_out

def m2mstr_object_hook_list(list_in):
    list_out = M2MList()
    for v in list_in:
        v = m2mstr_object_hook(v)
        list_out.append(v)
    return list_out

#
# Test cases
#
if __name__ == '__main__':
    path1 = M2MString("RootOper.Interfaces.InterfaceBrief({'InterfaceName': 'GigabitEthernet0/0/0/0'})")
    print(path1['InterfaceName'] + " == GigabitEthernet0/0/0/0")
    print(path1[0] + " == GigabitEthernet0/0/0/0")

    path2 = M2MString("RootCfg.InterfaceConfiguration({'Active': 'act', 'InterfaceName': 'GigabitEthernet0/0/0/0'}).Description")
    print(path2['InterfaceName'] + " == GigabitEthernet0/0/0/0")
    print(path2[1] + " == GigabitEthernet0/0/0/0")



