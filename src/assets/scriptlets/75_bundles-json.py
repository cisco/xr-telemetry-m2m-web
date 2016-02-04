# Map bundle interfaces to member ports

members = defaultdict(list)
for path, value in get("RootCfg.InterfaceConfiguration(*).BundleMember.ID"):
    members["Bundle-Ether" + str(value['BundleID'])].append(path['InterfaceName'])

print(members)
