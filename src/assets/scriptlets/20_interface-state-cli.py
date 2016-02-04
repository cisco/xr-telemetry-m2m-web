# Basic interface state using JSON CLI

for path, oper_state in cli_get('show int br'):
    print(path['InterfaceName'], oper_state['MTU'], oper_state['ActualState'])
