# Basic interface state with filtering

oper_intf_path = 'RootOper.Interfaces.InterfaceBrief(["tunnel-te*"])'
for path, oper_state in get(oper_intf_path):
    print(path['InterfaceName'], oper_state['MTU'], oper_state['ActualState'])



 # [Show this really tracks interface state]