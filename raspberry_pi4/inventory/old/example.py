#!/Users/ninja/.pyenv/shims/python
# coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

'''
Example custom dynamic inventory script for Ansible, in Python.
'''
import os
import sys
import argparse
import yaml

try:
    import json
except ImportError:
    import simplejson as json

from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.inventory.helpers import sort_groups, get_group_vars


def merge_two_dicts(x, y):
    """Merged dictionnary with X and Y"""
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


class ExampleInventory(object):

    def __init__(self, inventoryFile, variables=['ansible_host'], groups=['all']):
        self.inventory = {}
        self.variables = variables
        self.read_cli_args()
        self.groups = groups
        self.result = dict()
        self.loader = DataLoader()
        self.ansible_inventory = InventoryManager(loader=self.loader, sources=inventoryFile)
        self.variable_manager = VariableManager(loader=self.loader, inventory=inventoryFile)

        x = self.variable_manager._group_vars_files
        print(x)


        for grp in self.groups:
            for host in self.ansible_inventory.groups[grp].get_hosts():
                self.host = host.name
                self.groups = host.groups
                print(self.host, grp, host.vars)
        input("-ENTER-")

        print(self.variable_manager)
        print("-ENTER-")

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.example_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()
        # print(json.dumps(self.inventory));

    # Example inventory for testing.
    def example_inventory(self):
        return {
            'group': {
                'hosts': ['192.168.28.71', '192.168.28.72'],
                'vars': {
                    'ansible_ssh_user': 'vagrant',
                    'ansible_ssh_private_key_file':
                        '~/.vagrant.d/insecure_private_key',
                    'example_variable': 'value'
                }
            },
            '_meta': {
                'hostvars': {
                    '192.168.28.71': {
                        'host_specific_var': 'foo'
                    },
                    '192.168.28.72': {
                        'host_specific_var': 'bar'
                    }
                }
            }
        }

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

    def inventory_vars(self):
        for group in self.groups:
            # Set hosts list.
            hostsList = self.ansible_inventory.groups[group].get_hosts()
            for host in hostsList:
                var_list = list()
                # If you want to print all host attributes you can do this:
                # print(host.__dict__)

                # Set some variables for each host from inventory.
                name = host.name
                inGroups = host.groups
                group_vars = dict()
                for group_membership in host.groups:
                    group_vars = merge_two_dicts(
                        x=group_vars, y=group_membership.vars)
                for custom_variable in self.variables:
                    ansible_value = 'NOT_FOUND'
                    if custom_variable in group_vars:
                        ansible_value = group_vars[custom_variable]
                    if custom_variable in host.vars:
                        ansible_value = host.vars[custom_variable]
                    var_list.append({custom_variable: ansible_value})
                self.result[host] = var_list
        return self.result




# Get the inventory.
# ExampleInventory()

def read_ini_source(source):
    result = {}
    group = ""
    if os.path.isfile(source):
        with open(source, "r") as f:
            for line in f.readlines():
                line = line.strip()
                host = ()
                if "[" in line:
                    line = line.replace("[", "")
                    group = line.replace("]", "")
                elif "=" in line and len(group) != 0:
                    hostname = line.split(" ")[0]
                    ipaddr = line.split(" ")[1].split("=")[1]
                    username = line.split(" ")[2].split("=")[1]
                    result.setdefault(group, {})
                    result.setdefault('_meta', {})
                    result['_meta'].setdefault('hostvars', {})
                    if len(ipaddr) != 0:
                        result['_meta']['hostvars'].setdefault(ipaddr,{})
                        result['_meta']['hostvars'][ipaddr].setdefault('ansible_user', username)
                    result[group].setdefault('hosts', [])
                    result[group]['hosts'].append(ipaddr) 
                    result[group].setdefault('vars', {})
    print(json.dumps(result, indent=4))
    return result   


i  = ExampleInventory("/Users/ninja/ansible/inventory/inventory.ini")
i.inventory_vars()               
                    
                    
