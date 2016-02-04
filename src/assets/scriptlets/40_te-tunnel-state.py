# Assemble a "show interface brief" for signalled-named TE tunnels

sig_name_path = 'RootCfg.InterfaceConfiguration(*).TunnelTEAttributes.SignalledName'
for path, sig_name in get(sig_name_path):
    intf_name = path['InterfaceName']
    oper_state = get('RootOper.Interfaces.InterfaceBrief(["{}"])', intf_name).val
    print(sig_name, oper_state['MTU'], oper_state['ActualState'])
