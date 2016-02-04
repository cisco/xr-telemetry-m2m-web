# Map bundle interfaces to member ports

for path, value in get("RootCfg.InterfaceConfiguration(*).BundleMember.ID"):
    print('Bundle-Ether', value['BundleID'], ':', path['InterfaceName'])
