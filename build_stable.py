#!/usr/local/bin/python
# Author: Scott Chubb scott.chubb@netapp.com Justin Hover justin.hover@netapp.com
# Date: 22-Jan-2018
# Version 2.1
# https://www.github.com/schubb2003
# Notes: This script has been written for python 2.7.14 and 3.6.3
# on 2.7 you must install requests and ipaddress
# PEP8 compliance reviewed 7-Dec-2017
# Script is currently written to read a csv called cvfile for node information
# It then parses and builds the node information from said csv
# Format should be as below
# DhcpIP,1Gb_IP,1G_mask,1g_gateway,1G_DNSservers,10Gb_IP,10G_mask,10Gb_gateway,10G_MTU,NodeName
# Script expects arguments for cluster build information
# Args are as follows:
# Clustername,MVIP,SVIP,cluster admin, cluster admin password
# Usage: python build_stable.py sfdemo1 192.168.0.101 192.168.0.130 admin Netapp1!
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
from solidfire.models import Drive


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

# If not using CSV file, uncomment lines and change length check to 16
# and swap commenting on Insufficient arguments line
# Note: the logic does not currently exist to complete build without CSV
if len(sys.argv) < 6:
	# print("Insufficient arguments: DHCP|1Gb IP|1Gb netmask|1Gb gateway" + \
    # "|10Gb IP|10Gb netmask|10Gb gateway|10Gb MTU|DNS server(s)" + \
    # "|Nodename|Clustername|MVIP IP|User|Password")
    print("Insufficient arguments: Clustername|MVIP IP|SVIP IP|User|Password")
else:
    # DhcpIP = sys.argv[1]
    # StaticIP1G = sys.argv[2]
    # Netmask1G = sys.argv[3]
    # Gateway1G = sys.argv[4]
    # StaticIP10G = sys.argv[5]
    # Netmask10G = sys.argv[6]
    # Gateway10G = sys.argv[7]
    # MTU10G = sys.argv[8]
    # NameServers1G = sys.argv[9]
    # NodeName = sys.argv[10]
    ClusterName = sys.argv[1]
    mvipIP = sys.argv[2]
    svipIP = sys.argv[3]
    SFUser = sys.argv[4]
    SFUserPass = sys.argv[5]

# Web/REST auth credentials build authentication
auth = ("fake:fake")
encodeKey = base64.b64encode(auth.encode('utf-8'))
basicAuth = bytes.decode(encodeKey)


try:
    y = 0
    nodeArray = []
    with open("csvfile.csv", "rb") as buildFile:
        reader = csv.reader(buildFile, delimiter=",")
        for i, line in enumerate(reader):
           nodeCount = y + i
           DhcpIP = line[0]
           StaticIP1G = line[1]
           Netmask1G = line[2]
           Gateway1G = line[3]
           NameServer1G = line[4]
           StaticIP10G = line[5]
           Netmask10G = line[6]
           MTU10G = line[7]
           NodeName = line[8]
    # Verify submissions are valid IP addresses
    # Warning: this may break on Python versions above 3.x
           if sys.version_info.major == 2:
                ipaddress.ip_address(bytearray(DhcpIP))
                ipaddress.ip_address(bytearray(StaticIP1G))
                ipaddress.ip_address(bytearray(Netmask1G))
                ipaddress.ip_address(bytearray(Gateway1G))
                ipaddress.ip_address(bytearray(NameServer1G))
                ipaddress.ip_address(bytearray(StaticIP10G))
                ipaddress.ip_address(bytearray(Netmask10G))
           else:
                ipaddress.ip_address(DhcpIP)
                ipaddress.ip_address(StaticIP1G)
                ipaddress.ip_address(Netmask1G)
                ipaddress.ip_address(Gateway1G)
                ipaddress.ip_address(NameServer1G)
                ipaddress.ip_address(StaticIP10G)
                ipaddress.ip_address(Netmask10G)

    # Vars used later
           buildMipi = "" 	# Used in cluster build while loop
           buildSipi = "" 	# Used in cluster build while loop

    # Print output of submitted information
           print("Configuring cluster: \t" + ClusterName +
          "\nConfigure via node: \t" + NodeName +
          "\nConfigure via DHCP: \t" + DhcpIP +
          "\nConfigure 1G IP: \t" + StaticIP1G +
          "\nConfigure 1G netmask: \t" + Netmask1G +
          "\nConfigure 1G gateway: \t" + Gateway1G +
          "\nConfigure 10G IP: \t" + StaticIP10G +
          "\nConfigure 10G netmask: \t" + Netmask10G)

    # Ping the node DHCP address
           testIP(DhcpIP)

           sfe = ElementFactory.create(DhcpIP + ":442", "fake", "fake")

    # Apply configuration to node: 1G, 10G, cluster
           sfe.set_network_config(network=Network(bond1_g=NetworkConfig(address=StaticIP1G, netmask=Netmask1G, gateway=Gateway1G, dns_nameservers=NameServer1G)))
           sfe.set_network_config(network=Network(bond10_g=NetworkConfig(address=StaticIP10G, netmask=Netmask10G, mtu=MTU10G, bond_mode="LACP")))
           sfe.set_cluster_config(cluster=ClusterConfig(name=NodeName, cluster=ClusterName))
        
    # Place 10G IP in array for later cluster creation
           nodeArray.append(StaticIP10G)

    while buildMipi != 'Bond1G' and buildSipi != 'Bond10G':
        get_cluster_config_result = sfe.get_cluster_config()
        buildMipi = get_cluster_config_result.cluster.mipi
        buildSipi = get_cluster_config_result.cluster.sipi

# Cluster section
finally:
    
    sfe = ElementFactory.create(StaticIP1G, SFUser,SFUserPass, print_ascii_art="False")

    # Build the cluster config

    sfe.create_cluster(mvip=mvipIP, svip=svipIP, username=SFUser, password=SFUserPass, nodes=nodeArray, rep_count=2, accept_eula="true")
    print("Creating cluster: {} ".format(ClusterName))
    time.sleep(300)
    
    # Ping MVIP before proceeding
    testIP(mvipIP)

    # Build array of available drives and add them
    driveArray = []
    sfe = ElementFactory.create(mvipIP, SFUser, SFUserPass, print_ascii_art="False")
    list_drives = sfe.list_drives()
    for disk in list_drives.drives:
        if disk.status == "available":
            driveArray.append(disk.drive_id)
    sfe.add_drives(driveArray)
    print("Adding all available drives...")
    time.sleep(60)

#except requests.exceptions.SSLError:
    #print("SSL certificate error")
    print("Cluster Configuration Complete")
