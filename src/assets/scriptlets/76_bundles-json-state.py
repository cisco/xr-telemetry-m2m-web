# Map bundle interfaces to member ports with state

def state(intf):
    return get("RootOper.Interfaces.InterfaceBrief(['{}'])", intf).val["ActualState"]

members = defaultdict(list)
for path, value in get("RootCfg.InterfaceConfiguration(*).BundleMember.ID"):
    members["Bundle-Ether" + str(value['BundleID'])].append([path['InterfaceName'], state(path['InterfaceName'])])

print(members)
