##### OSX
#!/Users/ninja/.pyenv/shims/python

##### Linux
##### #!/usr/bin/env python3

try:
    import ansible.constants as C
    from ansible.parsing.dataloader import DataLoader
    from ansible.inventory.manager import InventoryManager
    from ansible.vars.manager import VariableManager
    import os
    import sys
    import json
    import nmap
    import yaml
except ImportError:
    print("Module not found. Please install it.")

def get_inventory_config(base_path, extension):
    '''scans base path for inventory.yaml config file'''
    try:
        for root, dirs, files in os.walk(base_path):
            if "inventory" in root:
                for file in files:
                    if "inventory" in file and file.endswith(extension):
                        return os.path.join(root, file)
    except FileNotFoundError as err:
        print("Inventory file not found. Please check if config file is in place.")

def convert_ip_range(cnf):
    '''converts dot notation like 255.255.255.0 into cidr like /24 notation'''
    start_ip = cnf['range'][0]
    end_ip = cnf['range'][1]
    cidr = subnet_mask_to_cidr(cnf['subnet'])
    return start_ip.replace('0.2','0.0'+cidr)

def scan_assets(subnet, port=22):
    '''nmap scans for online hosts with open ssh port'''
    nm = nmap.PortScanner()
    nm.scan(hosts=subnet, arguments='-p'+str(port))
    live_hosts = []
    for host in nm.all_hosts():
        print()
        if nm[host]['status']['state'] == 'up' and \
            nm[host]['tcp'][22]['state'] == "open":
            live_hosts.append(host)
    return live_hosts

#def scan_assets(inventory_src='/Users/ninja/ansible/inventory'):
    # Use Ansible's Python API to gather inventory information
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=inventory_src)

    # Return the list of hosts
    return inventory.get_hosts()

def add_new_host(host_name, group_name, host_vars=None):
    # Add a new host to the inventory manager
    loader = DataLoader()
    inventory_manager = InventoryManager(loader=loader)
    new_host = inventory_manager.add_host(host_name)
    if group_name:
        inventory_manager.add_group(group_name)
        inventory_manager.add_host(host_name, group_name)

    if host_vars:
        for key, value in host_vars.items():
            new_host.set_variable(key, value)
    return (loader, inventory_manager)

def get_host_vars(host, inventory_src='/Users/ninja/ansible/inventory'):
    # Use Ansible's Python API to get host variables
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=inventory_src)
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    
    # Get variables for the specified host
    return variable_manager.get_vars(host=host)

def get_group_vars(loader, inventory_src):
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=inventory_src)
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    
    # Get group variables
    group = inventory.get_group(group_name)
    group_vars = variable_manager.get_vars(group=group)

def generate_host_vars(host):
    # Generate host variables
    # Modify this function as needed to generate host variables
    return {}

def generate_group_vars():
    # Generate group variables
    # Modify this function as needed to generate group variables
    return {}

def read_inventory_configuration(cnf, search):
    '''searches dict keys in yaml config file'''
    try:
        if os.path.isfile(cnf):
            with open(cnf, "r") as config_file:
                data = yaml.safe_load(config_file)
                for key in data.keys():
                    if search in key:
                        return data[key]
    except (FileNotFoundError, yaml.YAMLError, KeyError) as exc:
        print(f"Error: {exc}")

def subnet_mask_to_cidr(subnet_mask):
    # Split the subnet mask into octets
    octets = subnet_mask.split('.')
    
    # Initialize the CIDR notation counter
    cidr = 0
    
    # Iterate through each octet and count the number of set bits
    for octet in octets:
        # Convert the octet to its binary representation
        binary_octet = bin(int(octet))[2:].zfill(8)
        
        # Count the number of set bits in the binary octet
        cidr += binary_octet.count('1')
    
    return '/' + str(cidr)

def main():
    extention = ".yaml"
    inventory_dir = os.path.join(os.getcwed(), "inventory")
    inventory_config = get_inventory_config(inventory_dir, extention)
    config_data = read_inventory_configuration(inventory_config, "network")
    ip_range = convert_ip_range(config_data, "network")
    hostlist = scan_assets(ip_range, port=22)
    
    print(hostlist)
    
    #TODO: add hostlist into ansible inventory
    # add_new_host(host_name, group_name, host_vars=None)
    
    
    """ loader = DataLoader()
    inventory_manager = InventoryManager(loader=loader, sources=inventory_src)
    variable_manager = VariableManager(loader=loader, inventory=inventory_manager)    
    
    subnet = "192.168.0.0/24"
    check_port = 22
    hosts = scan_assets(subnet, check_port)
    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "hosts": [],
            "children": []
        }
    }
    
    # Populate host variables
    for host in hosts:
        host_vars = get_host_vars(host)
        inventory["_meta"]["hostvars"][host.name] = host_vars
        inventory["all"]["hosts"].append(host.name)
    
    print(json.dumps(inventory))
 """
if __name__ == "__main__":
    main()
