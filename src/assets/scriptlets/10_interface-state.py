# Basic interface state

oper_intf_path = 'RootOper.Interfaces.InterfaceBrief'
for path, oper_state in get(oper_intf_path):
    print(path['InterfaceName'], oper_state['MTU'], oper_state['ActualState'])
