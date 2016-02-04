## Retrieving structured operational data in a custom format

for path, data in get('RootOper.EthernetInterface.Interface'):
    print(path['InterfaceName'], 
          data['Layer1Info']['LEDState'], 
          data['MacInfo']['OperationalMACAddress'])