#!/usr/local/bin/python
# Author: Scott Chubb scott.chubb@netapp.com, Justin Hover justin.hover@netapp.com
# No warranty is provided, use at your own risk
# Updates are uploaded at modification time, testing may not have occurred
# Never run scripts in production without testing in non-prod prior
# Date: 8-Feb-2018
# Version 2.4
# Notes: This script has been written for python 3.4 and above
# Script is currently written to read a csv called csvfile for information
# It then parses and builds the node information from said csv
# Format should be as below
# dhcpIP(if used),1Gb_IP,1G_mask,1g_gateway,1G_DNSservers,
#   10Gb_IP,10G_mask,10G_MTU,nodeName
# Script expects arguments for cluster build information
# Args are as follows:
# Clustername,MVIP,SVIP,cluster admin, cluster admin password (change DHCP IPs) (converge managment IPs)
# Usage: python build.py -cn sfdemo1 -mv 192.168.0.101 -sv 192.168.0.130 -un admin -pw Netapp1! (-ud | -nd) (-cm | -nc)

import sys
import os
import csv
import ipaddress
import time
import argparse
from platform import system as system_name
from subprocess import call
from solidfire.factory import ElementFactory
from solidfire.models import Drive

parser = argparse.ArgumentParser()
parser.add_argument('-cn', type=str,
                    required=True,
                    metavar='clustername',
                    help='cluster name')    
parser.add_argument('-mv', type=ipaddress.ip_address,
                    required=True,
                    metavar='mvip',
                    help='MVIP name or IP')
parser.add_argument('-sv', type=ipaddress.ip_address,
                    required=True,
                    metavar='svip',
                    help='SVIP name or IP')                    
parser.add_argument('-un', type=str,
                    required=True,
                    metavar='username',
                    help='username to connect with')
parser.add_argument('-pw', type=str,
                    required=True,
                    metavar='password',
                    help='password for user')
dhcp_parser = parser.add_mutually_exclusive_group(required=True)
dhcp_parser.add_argument('-ud', '--dhcp',
                    dest='dhcp',
                    help='update 1G IPs from dhcp',
                    action='store_true')
dhcp_parser.add_argument('-nd', '--no-dhcp',
                    dest='dhcp',
                    help='dhcp IPs not in use, do not change existing',
                    action='store_false')
converge_parser = parser.add_mutually_exclusive_group(required=True)
converge_parser.add_argument('-cm',
                    '--converge-mgmt',
                    dest='converge-mgmt',
                    help='Configure management on 10G in place of 1G',
                    action='store_true')
converge_parser.add_argument('-nc',
                    '--no-converge-mgmt',
                    dest='converge_mgmt',
                    help='Configure management on 1G',
                    action='store_false')
parser.set_defaults(dhcp=True)
parser.set_defaults(converge_mgmt=False)
args = parser.parse_args()

cluster_name = args.cn
mvip_ip = args.mv
svip_ip = args.sv
sf_user = args.un
sf_user_pass = args.pw
update_dhcp_addr = args.ud
network_converge = args.cm


# Vars used later
build_mipi = ""
build_sipi = ""
node_count = 0
node_array = []


# Function to build array of available drives and add them
def drive_add():
    drive_array = []
    check_array = []
    sfe_drive_add = ElementFactory.create(mvip_ip,
                                         sf_user,
                                         sf_user_pass,
                                         print_ascii_art=False)
    list_drives = sfe_drive_add.list_drives()
    for disk in list_drives.drives:
        if disk.status == "available":
            drive_array.append(disk.drive_id)
    sfe_drive_add.add_drives(drive_array)
    sys.stdout.write("Sleep 300 seconds while adding all available drives...")
    time.sleep(300)
    
    check_drives = sfe_drive_add.list_drives()
    for disk in check_drives.drives:
        if disk.status != "available":
            check_array.append(disk.drive_id)
            if len(check_array) > 0:
                sys.stdout.write("Error assigning drives %s, " % check_array + \
                                 "please double check drive status")

# Function used to determine if the OS is Windows or Unix and test ping
def test_ip(host):
    ping_loop_count = 0
    if system_name().lower() == "windows":
            response = os.system("ping -n 2 " + host)
    else:
            response = os.system("ping -c 2 " + host)
    sys.stdout.write(response)
    while response != 0:
            sys.stdout.write("retrying...")
            time.sleep(10)
            ping_loop_count += 1
            if ping_loop_count >= 10:
                sys.exit("PING loop count exceeds 10 tries, "
                         "script exiting, build incomplete")

# Function to determine if input is a valid IP address, this works for IPv4 and IPv6 
# This script explicity calls out Python v2 and above as valid and below v2 as unsupported
# Changes to Python in the future could result in the script needing updated to address that                   
def verify_ip(addr):
    if sys.version_info[0] == 2:
        try:
            ipaddress.ip_address(bytearray(addr))
        except ValueError:
            sys.exit("Input does not evaluate to an IP address for node "
                     "%s, submitted IP is %s" % (nodeName,addr))
    elif sys.version_info[0] > 2:
        try:
            ipaddress.ip_address(addr)
        except ValueError:
            sys.exit("Input does not evaluate to an IP address for node "
                     "%s, submitted IP is %s" % (nodeName,addr))
    elif sys.version_info[0] < 2:
        sys.exit("Unsupported version of Python detected, script will exit")

# Function to wait until mipi and sipi are on the proper networks
def ipi_check():
    net_int_loop_check = 0
    get_cluster_config_result = sfe.get_cluster_config()
    build_mipi = get_cluster_config_result.cluster.mipi
    build_sipi = get_cluster_config_result.cluster.sipi
    net_int_loop_check += 1
    if net_int_loop_check > 10:
        sys.exit("MVIP/SVIP verification exceeded 10 tries, "
                 " on host %s. script has exited, " % nodeName + \
                 "build state incomplete")


try:
    with open("csvfile.csv", "r") as buildFile:
        reader = csv.reader(buildFile, delimiter=",")
        for i, line in enumerate(reader):
            node_count += 1
            if dhcp is True:
                dhcpIP = line[0]
                staticIP1G = line[1]
                netmask1G = line[2]
                gateway1G = line[3]
                nameServer1G = line[4]
                staticIP10G = line[5]
                netmask10G = line[6]
                MTU10G = line[7]
                nodeName = line[8]
            else:
                staticIP1G = line[0]
                netmask1G = line[1]
                gateway1G = line[2]
                nameServer1G = line[3]
                staticIP10G = line[4]
                netmask10G = line[5]
                MTU10G = line[6]
                nodeName = line[7]
                
                # comment dhcpIP out if 1GbE IPs are static configured prior
                verify_ip(dhcpIP)
                verify_ip(staticIP1G)
                verify_ip(netmask1G)
                verify_ip(gateway1G)
                verify_ip(nameServer1G)
                verify_ip(staticIP10G)
                verify_ip(netmask10G)

            if dhcp is True:
                sys.stdout.write("Configuring cluster: \t" + cluster_name +
                      "\nConfigure via node: \t" + nodeName +
                      "\nConfigure via DHCP: \t" + dhcpIP +
                      "\nConfigure 1G IP: \t" + staticIP1G +
                      "\nConfigure 1G netmask: \t" + netmask1G +
                      "\nConfigure 1G gateway: \t" + gateway1G +
                      "\nConfigure 10G IP: \t" + staticIP10G +
                      "\nConfigure 10G netmask: \t" + netmask10G)
            else:
                sys.stdout.write("Configuring cluster: \t" + cluster_name +
                      "\nConfigure via node: \t" + nodeName +
                      "\nConfigure 1G IP: \t" + staticIP1G +
                      "\nConfigure 1G netmask: \t" + netmask1G +
                      "\nConfigure 1G gateway: \t" + gateway1G +
                      "\nConfigure 10G IP: \t" + staticIP10G +
                      "\nConfigure 10G netmask: \t" + netmask10G)

            # Change to staticIP1G if 1GbE IPs are static configured prior
            test_ip(dhcpIP)

            # Change dhcpIP to staticIP1G if 1GbE IPs are static configured prior
            sfe = ElementFactory.create(dhcpIP + ":442",
                                        "fake",
                                        "fake",
                                        print_ascii_art=False)
        # Apply configuration to node: 1G, 10G, cluster
        # comment below line out if 1GbE IPs are static configured prior
        # If the IP is set, but DNS servers need applied remove all line except dns_namservers=nameServer1G
            if dhcp is True and converge_mgmt is False:
                sfe.set_network_config(network=Network(bond1_g=NetworkConfig(address=staticIP1G,
                                                                             netmask=netmask1G,
                                                                             gateway=gateway1G,
                                                                             dns_nameservers=nameServer1G)))
            sfe2 = ElementFactory.create(staticIP1G + ":442",
                                         sf_user,
                                         sf_user_pass,
                                         print_ascii_art=False)
            sfe2.set_network_config(network=Network(bond10_g=NetworkConfig(address=staticIP10G,
                                                                           netmask=netmask10G,
                                                                           mtu=MTU10G,
                                                                           bond_mode="LACP")))
            sfe2.set_cluster_config(cluster=ClusterConfig(name=nodeName, 
                                                          cluster=cluster_name))

        # Place 10G IP in array for later cluster creation
            node_array.append(staticIP10G)
            if converge_mgmt is True:
                while build_mipi != 'Bond1G' and build_sipi != 'Bond10G':
                    ipi_check()
            else:
                while build_mipi != 'Bond10G' and build_sipi != 'Bond10G':
                    ipi_check()

# Cluster section
finally:
    time.sleep(30)
    sfe3 = ElementFactory.create(staticIP1G,
                                 sf_user,
                                 sf_user_pass,
                                 timeout=300)

    # Build the cluster config
    
    # rep_count=2 is the code for double helix
    # IF triple helix is ever implemented, adjust this to three
    # for triple write protection, quad helix set to 4, etc
    sfe3.create_cluster(mvip=mvip_ip,
                        svip=svip_ip,
                        username=sf_user,
                        password=sf_user_pass,
                        nodes=node_array,
                        rep_count=2,
                        accept_eula="True")
    sys.stdout.write("Creating cluster " + cluster_name)

    # Ping MVIP before proceeding
    test_ip(mvip_ip)

    cluster_state = sfe3.get_cluster_state
    # Check cluster nodes equal the expected number
    # Generate output if there is any mismatch detected and note the mismatch
    node_count = 0
    node_count_compare = 0
    for node in cluster_state.nodes:
        if node.result.state == "Active":
            node_count_compare += 1
    if node_count_compare < node_count and node_count_compare > 0:
        drive_add()
        sys.exit("Node count less than expected"
                 "\nNode count should be {}"\
                 "\nNode count returned from cluster is {}"
                 "\nScript has exited, build is "
                 "partially completed".format(node_count, node_count_compare))
    elif node_count_compare > node_count:
        drive_add()
        sys.exit("Node count greater than expected"
                 "\nNode count should be {}"
                 "\nNode count returned from cluster is {}"
                 "\nScript has exited, build "
                 "state unknown".format(node_count, node_count_compare))
    elif node_count_compare == 0:
        sys.exit("Node count mismatch detected, node count is zero"
                 "\nNode count should be {}"
                 "\nNode count returned from cluster is {}"
                 "\nScript has exited, build "
                 "does not appear complete".format(node_count, node_count_compare))

    else:
        drive_add()
        sys.stdout.write("Cluster Configuration Complete")
