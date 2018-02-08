#!/usr/local/bin/python
# Author: Scott Chubb scott.chubb@netapp.com, Justin Hover justin.hover@netapp.com
# Date: 25-Jan-2018
# Version 2.2
# Script is currently written to read a csv called cvfile for node information
# It then parses and builds the node information from said csv
# Format should be as below
# DhcpIP,1Gb_IP,1G_mask,1g_gateway,1G_DNSservers,10Gb_IP,10G_mask,10G_MTU,NodeName
# Script expects arguments for cluster build information
# Args are as follows:
# Clustername,MVIP,SVIP,cluster admin, cluster admin password
# Usage: python build_2.py sfdemo1 192.168.0.101 192.168.0.130 admin Netapp1!
import sys
import base64
import os
import requests
import csv
import ipaddress
import time
from platform import system as system_name
from subprocess import call
from solidfire.factory import ElementFactory
from solidfire.models import *


# Function used to determine if the OS is Windows or Unix for testPing
def testIP(host):
        if system_name().lower() == "windows":
                response = os.system("ping -n 2 " + host)
        else:
                response = os.system("ping -c 2 " + host)
        print(response)
        while response != 0:
                print("retrying...")
                time.sleep(10)
                
# Function to determine if input is a valid IP address, this works for IPv4 and IPv6 
# This script explicity calls out Python v2 and above as valid and below v2 as unsupported
# Changes to Python in the future could result in the script needing updated to address said changes                   
def verifyIP(addr):
    if sys.version_info[0] == 2:
        try:
            verifyIP(addr))
        except ValueError:
            sys.exit("Input does not evaluate to an IP address for node %s, submitted IP is %s" % (NodeName,addr))
    elif sys.version_info[0] > 2:
        ipaddress.ip_address(addr)
        except ValueError:
            sys.exit("Input does not evaluate to an IP address for node %s, submitted IP is %s" % (NodeName,addr))
    elif sys.version_info[0] < 2:
        sys.exit("Unsupported version of Python detected, script will exit")

if len(sys.argv) < 6:
    print("Insufficient arguments: Clustername|MVIP IP|SVIP IP|User|Password")
else:
    # DhcpIP = sys.argv[1]
    # StaticIP1G = sys.argv[2]
    # Netmask1G = sys.argv[3]
    # Gateway1G = sys.argv[4]
    # StaticIP10G = sys.argv[5]
    # Netmask10G = sys.argv[6]
    # MTU10G = sys.argv[7]
    # NameServers1G = sys.argv[8]
    # NodeName = sys.argv[9]
    ClusterName = sys.argv[1]
    mvipIP = sys.argv[2]
    svipIP = sys.argv[3]
    SFUser = sys.argv[4]
    SFUserPass = sys.argv[5]

try:
    nodeArray = []
    with open("csvfile.csv", "r") as buildFile:
        reader = csv.reader(buildFile, delimiter=",")
        for i, line in enumerate(reader):
            nodeCount = 1 + i
            # If using static IPs comment out DhcpIP line and adjust numbering on the remaining lines
            DhcpIP = line[0]
            StaticIP1G = line[1]
            Netmask1G = line[2]
            Gateway1G = line[3]
            NameServer1G = line[4]
            StaticIP10G = line[5]
            MTU10G = line[6]
            NodeName = line[7]
    # Verify submissions are valid IP addresses
            # If using static IPs comment out DhcpIP line and adjust numbering on the remaining lines
            verifyIP(DhcpIP)
            verifyIP(StaticIP1G)
            verifyIP(Netmask1G)
            verifyIP(Gateway1G)
            verifyIP(NameServer1G)
            verifyIP(StaticIP10G)
            verifyIP(Netmask10G)

    # Vars used later
            buildMipi = "" 	# Used in cluster build while loop
            buildSipi = "" 	# Used in cluster build while loop

    # Print output of submitted information
            print("Configuring cluster: \t" + ClusterName +
                  "\nConfigure via node: \t" + NodeName +
                  #If using static IPs comment out the DHCP line below
                  "\nConfigure via DHCP: \t" + DhcpIP +
                  "\nConfigure 1G IP: \t" + StaticIP1G +
                  "\nConfigure 1G netmask: \t" + Netmask1G +
                  "\nConfigure 1G gateway: \t" + Gateway1G +
                  "\nConfigure 10G IP: \t" + StaticIP10G +
                  "\nConfigure 10G netmask: \t" + Netmask10G)

    # Ping the node DHCP address
            # If using static IPs change DhcpIP to StaticIP1G for both lines below
            testIP(DhcpIP)
            
            sfe = ElementFactory.create(DhcpIP + ":442", "fake", "fake", print_ascii_art="False")

    # Apply configuration to node: 1G, 10G, cluster
            # If using static IPs comment out the bond1_g line, **NOTE** you may need to configure DNS servers separately
            sfe.set_network_config(network=Network(bond1_g=NetworkConfig(address=StaticIP1G, netmask=Netmask1G, gateway=Gateway1G, dns_nameservers=NameServer1G)))
            sfe2 = ElementFactory.create(StaticIP1G + ":442", SFUser, SFUserPass, print_ascii_art="false")
            sfe2.set_network_config(network=Network(bond10_g=NetworkConfig(address=StaticIP10G, netmask=Netmask10G, mtu=MTU10G, bond_mode="LACP")))
            sfe2.set_cluster_config(cluster=ClusterConfig(name=NodeName, cluster=ClusterName))

    # Place 10G IP in array for later cluster creation
            nodeArray.append(StaticIP10G)

            while buildMipi != 'Bond1G' and buildSipi != 'Bond10G':
                get_cluster_config_result = sfe.get_cluster_config()
                buildMipi = get_cluster_config_result.cluster.mipi
                buildSipi = get_cluster_config_result.cluster.sipi

# Cluster section
finally:
    time.sleep(30)
    sfe3 = ElementFactory.create(StaticIP1G, SFUser, SFUserPass)
    sfe3.timeout(300)
    # Build the cluster config

    sfe3.create_cluster(mvip=mvipIP, svip=svipIP, username=SFUser, password=SFUserPass, nodes=nodeArray, rep_count=2, accept_eula="true")
    print("Creating cluster " + ClusterName)

    # Ping MVIP before proceeding
    testIP(mvipIP)

    # Build array of available drives and add them
    driveArray = []
    sfe4 = ElementFactory.create(mvipIP, SFUser, SFUserPass, print_ascii_art="false")
    list_drives = sfe.list_drives()
    for disk in list_drives.drives:
        if disk.status == "available":
            driveArray.append(disk.drive_id)
    sfe4.add_drives(driveArray)
    print("Adding all available drives...")
    time.sleep(60)

    print("Cluster Configuration Complete")
