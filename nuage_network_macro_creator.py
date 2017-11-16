#!/usr/bin/python
"""
Usage:
  nuage-network-macro-creator [options]
  nuage-network-macro-creator (-h | --help)
  
Options:
  -h --help              Show this screen
  -v --version           Show version
  --ipfile=<file>        IP List location
  --vsd=<string>         IP of VSD
  --enterprise=<string>  Enterprise name

"""

from docopt import docopt
from vspk import v5_0 as vsdk
import time
import sys
import ipaddr

def getargs():
    return docopt(__doc__, version="nuage-network-macro-creator 1.0.0")

def execute():
    main(getargs())

def main(args):
    api_url = "https://"+str(args['--vsd'])+":8443"
    try:
        session = vsdk.NUVSDSession(username='csproot', password='csproot', enterprise='csp', api_url=api_url)
        session.start()
        csproot = session.user
    except:
        print("ERROR: Could not establish connection to VSD API")
        sys.exit(1)

    print("Reading IP list from file ...")
    with open(str(args['--ipfile'])) as f:
        addresses = f.read().splitlines()
    print(" --- DONE\n")

    print("Fetching Enterprise object ...")
    filter_str = 'name == "'+str(args['--enterprise'])+'"'
    enterprise_test = csproot.enterprises.get_first(filter=filter_str)
    print(" --- DONE\n")

    print("Creating Network Macro Group ...")
    networkMacroGroupName = str(args['--ipfile'])
    networkMacroGroupName = networkMacroGroupName.replace('.txt','')
    networkMacroGroup = create_networkMacroGroup(enterprise_test,networkMacroGroupName)
    print(" --- DONE\n")

    print("Creating Network Macros and attaching them to the Network Macro Group ...")
    for address in addresses:
        networkMacro = create_networkMacro(enterprise_test,ipaddr.IPv4Network(address))
        assign_networkMacro_to_networkMacroGroup(networkMacroGroup,networkMacro)
    print(" --- DONE\n")
 
def create_networkMacroGroup(enterprise, MacroGroupName):
    networkMacroGroup = vsdk.NUNetworkMacroGroup(name=MacroGroupName)
    enterprise.create_child(networkMacroGroup)
    return networkMacroGroup

def create_networkMacro(enterprise, ipaddress):  
    name = str(ipaddress.ip)
    networkMacro = vsdk.NUEnterpriseNetwork(ip_type="IPV4", netmask= str(ipaddress.netmask), address= str(ipaddress.ip), name=name.replace('.', ''))
    enterprise.create_child(networkMacro)
    return networkMacro

def assign_networkMacro_to_networkMacroGroup(networkMacroGroup, networkMacro):
    networkMacroGroup.enterprise_networks.get()
    networkMacroGroup.assign([networkMacro] + networkMacroGroup.enterprise_networks,vsdk.NUEnterpriseNetwork)
    return networkMacroGroup
 
if __name__ == "__main__":
    main(getargs())


 

 