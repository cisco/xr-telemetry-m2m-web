# =============================================================================
# scrape.py
#
# This file implements some show command scrapers.
#
# December 2015
#
# Copyright (c) 2015 by cisco Systems, Inc.
# All rights reserved.
# =============================================================================

import re
from collections import OrderedDict

def commit_history(cli):
    """
    Parse output of "show configuration history commit reverse detail"
    """
    result = []
    record = OrderedDict()
    for line in cli.splitlines():
        r = re.search(' ([A-Z][a-z]+(?: ID)?): (.*?) +([A-Z][a-z]+): (.*)', line)
        if not r:
            continue
        record[r.group(1)] = r.group(2)
        record[r.group(3)] = r.group(4)
        if r.group(3) == 'Comment':
            result.append(record)
            record = OrderedDict()
    return result

def config_changes(cli):
    """
    Parse output of "show configuration commit changes <id>"
    """
    result = []
    in_config = False
    for line in cli.splitlines():
        if not in_config and line == 'Building configuration...':
            in_config = True
        elif in_config:
            result.append(line)

    return '\n'.join(result)

def schema_describe(cli, sdata):
    """
    Do a schema-describe and return the list of paths
    """
    d = sdata.api.cli_exec('schema-describe ' + cli)
    d.addCallback(lambda reply: \
                  re.findall('^Path: *(.*)$', reply['result'], re.MULTILINE))
    return d

#####################################################################################
#
# Tests
#
#####################################################################################

commit_history_test = '''\
Tue May 19 17:43:48.450 UTC
   1)  Event: commit         Time: Tue May 19 17:43:44 2015
       Commit ID: 1000000005 Label: 
       User: cisco           Line: vty0:node0_0_CPU0
       Client: Rollback      Comment: 

   2)  Event: commit         Time: Tue May 19 17:39:52 2015
       Commit ID: 1000000004 Label: 
       User: cisco           Line: vty0:node0_0_CPU0
       Client: CLI           Comment: 

   3)  Event: commit         Time: Tue May 19 17:38:09 2015
       Commit ID: 1000000003 Label: 
       User: cisco           Line: vty0:node0_0_CPU0
       Client: CLI           Comment: 

   4)  Event: commit         Time: Tue May 19 14:39:42 2015
       Commit ID: 1000000002 Label: 
       User: CVAC            Line: UNKNOWN
       Client: CLI           Comment: Auto-configured by Cisco Virtual Appliance Configuration

   5)  Event: commit         Time: Sun May 17 19:33:50 2015
       Commit ID: 1000000001 Label: 
       User: CVAC            Line: UNKNOWN
       Client: CLI           Comment: Auto-configured by Cisco Virtual Appliance Configuration

'''

config_changes_test = '''\
Tue May 19 17:44:12.478 UTC
Building configuration...
!! IOS XR Configuration 6.0.0.03I
interface GigabitEthernet0/0/0/0
!
end
'''

if __name__ == '__main__':
    import pprint
    pprint.pprint(commit_history(commit_history_test))
    print(config_changes(config_changes_test))
