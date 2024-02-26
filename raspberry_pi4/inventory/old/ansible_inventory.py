#!/Users/ninja/.pyenv/shims/python

import os
import sys
import json
import argparse

from ansible.parsing.dataloader import DataLoader
# from ssh_check import scanner

try:
    from ansible.inventory.manager import InventoryManager
    A24 = True
except ImportError:
    from ansible.vars import VariableManager
    from ansible.inventory import Inventory
    A24 = False

base_path = "/Users/ninja/ansible"
inventory_file = base_path + "/inventory/inventory.ini"
loader = DataLoader()

parser = argparse.ArgumentParser(description="CloudIQ Ansible Dynamic Inventory")
parser.add_argument("--list", help="Ansible inventory of all groups", action="store_true", dest="list_inventory")
parser.add_argument("--host", help="Specific host inventory. DEPRECATED: It only returns empty dict", action="store", dest="ansible_host", type=str)
cli_args = parser.parse_args()
list_inventory = cli_args.list_inventory
ansible_host = cli_args.ansible_host

if A24:
    if os.path.exists(inventory_file):
        inventory = InventoryManager(loader, [inventory_file])
    else:
        inventory = InventoryManager(loader, [sys.argv[1]])
    inventory.parse_sources()
else:
    variable_manager = VariableManager()
    inventory = Inventory(loader, variable_manager, sys.argv[1])
    inventory.parse_inventory(inventory.host_list)

out = {'_meta': {'hostvars': {}}}
for group in inventory.groups.values():
    out[group.name] = {
        'hosts': [h.name for h in group.hosts],
        'vars': group.vars,
        'children': [c.name for c in group.child_groups]
    }
for host in inventory.get_hosts():
    out['_meta']['hostvars'][host.name] = host.vars

print(json.dumps(out, indent=4, sort_keys=True))





