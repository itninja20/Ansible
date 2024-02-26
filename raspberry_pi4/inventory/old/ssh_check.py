#!/Users/ninja/.pyenv/shims/python
#
#   *** using custom python interpreter ***
#
import os
import os.path
import sys
import json
import configparser
import nmap
from ansible.parsing.dataloader import DataLoader


#def ini_files(ini_file):
#    config_object = configparser.ConfigParser()
#    try:
#        file = open(ini_file,"r")
#        config_object.read_file(file)
#        output_dict=dict()
#        sections=config_object.sections()
#        for section in sections:
#            items=config_object.items(section)
#            output_dict[section]=dict(items)
#            # print("The output dictionary is:")
#            # print(output_dict)
#        return output_dict
#    except FileNotFoundError as err:
#        print(err)

#_path = "/Users/ninja/ansible/inventory"
#_input = _path + "/inventory.ini"
#data = ini_files(_input)
#print(data)

def scanner(ip_range, port):
    results = []
    nm = nmap.PortScanner()
    nm.scan(hosts=ip_range, arguments='-T4 -sV -A -v -p'+str(port), sudo=True)
    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            print(host + ':\t' + str(nm[host].state()) \
                    + '\ttcp/22    ' \
                    + '[ ' + str(nm[host][proto][port]['state']) + ' ]')
            if "open" in nm[host][proto][port]['state']:
                results.append(host)
    return results

# Use:
#ip_range = "192.168.0.0/24"
#port = 22
#scanner(ip_range, port)




