#!/usr/local/bin/python
# Author: Scott Chubb scott.chubb@netapp.com
# Date: 6-Dec-2017
# Version 1.1
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
# Usage: python build_2.py sfdemo1 192.168.0.101 192.168.0.130 admin Netapp1!
import sys
import base64
import os
import requests
import csv
import ipaddress
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
    requests.request("GET", url)
    if response.status_code == 200:
        print("Connection is valid")
    elif response.status_code == 401:
        print("Authorization error, check username and password")
    elif response.status_code == 500:
        print("Invalid JSON data submitted")
    else:
        print("Error code:\t %s" % response.status_code)
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
                Gateway10G = line[7]
                MTU10G = line[8]
                NodeName = line[9]

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
        ipaddress.ip_address(bytearray(Gateway10G))
    else:
        ipaddress.ip_address(DhcpIP)
        ipaddress.ip_address(StaticIP1G)
        ipaddress.ip_address(Netmask1G)
        ipaddress.ip_address(Gateway1G)
        ipaddress.ip_address(NameServer1G)
        ipaddress.ip_address(StaticIP10G)
        ipaddress.ip_address(Netmask10G)
        ipaddress.ip_address(Gateway10G)

    # Vars used later
    y = 1 			# Used to compare node count to bootstrap list
    buildMipi = "" 	# Used in cluster build while loop
    buildSipi = "" 	# Used in cluster build while loop
    nurl = "https://" + DhcpIP + ":442/json-rpc/9.0"  # Node based url

    # Print output of submitted information
    print("Configuring cluster: \t" + ClusterName +
          "\nConfigure via node: \t" + NodeName +
          "\nConfigure via DHCP: \t" + DhcpIP +
          "\nConfigure 1G IP: \t" + StaticIP1G +
          "\nConfigure 1G netmask: \t" + Netmask1G +
          "\nConfigure 1G gateway: \t" + Gateway1G +
          "\nConfigure 10G IP: \t" + StaticIP10G +
          "\nConfigure 10G netmask: \t" + Netmask10G +
          "\nConfigure 10G gateway: \t" + Gateway10G)

    # Ping the node DHCP address
    testIP(DhcpIP)

    sfe = ElementFactory.create(DhcpIP, "fake", "fake")

    # Build the 1G networking
    network1GCfg = "{\n\t\"method\": \"SetNetworkConfig\"," \
                   "\n\t\" params\": { " \
                   "\n\t\t\"network\": {\"Bond1G\" :{" \
                   "\n\t\t\t\"address\": \"" + StaticIP1G + "\"," \
                   "\n\t\t\t\"netmask\": \"" + Netmask1G + "\"," \
                   "\n\t\t\t\"gateway\": \"" + Gateway1G + "\"," \
                   "\n\t\t\t\"nameservers\": \"" + NameServers1G + "\"" \
                   "\n    \t\t\t}\n\t\t}\n},\n    \"id\": 1\n}"

    # Build the 10G networking
    network10GCfg = "{\n\t\"method\": \"SetNetworkConfig\"," \
                    "\n\t\"params\": " \
                    "{\n\t\t\"network\": {\"Bond10G\" :{" \
                    "\n\t\t\t\"address\": \"" + StaticIP10G + "\"," \
                    "\n\t\t\t\"netmask\": \"" + Netmask10G + "\"," \
                    "\n\t\t\t\"gateway\": \"" + Gateway10G + "\"," \
                    "\n\t\t\t\"mtu\": \"" + MTU10G + "\"" \
                    "\n    \t\t\t}\n\t\t}\n},\n    \"id\": 1\n}"

    # Build the node cluster config
    nodeClusterCfg = "{\n\t\"method\": \"SetClusterConfig\"," \
                     "\n\t\"params\": {\n\t\t\"cluster\" :{" \
                     "\n\t\t\t\"cipi\": \"Bond10G\"," \
                     "\n\t\t\t\"cluster\": \"" + ClusterName + "\"," \
                     "\n\t\t\t\"mipi\": \"Bond1G\"," \
                     "\n\t\t\t\"sipi\": \"Bond10G\"," \
                     "\n    \t\t\t}\n\t\t},\n   \"id\": 1\n}"

    headers = {
               'content-type': "application/json",
               'authorization': "Basic " + basicAuth
               }

    response10G = requests.request("POST",
                                   nurl,
                                   data=network10GCfg,
                                   headers=headers,
                                   verify=False)

    testPing(StaticIP10G)

    response1G = requests.request("POST",
                                  nurl,
                                  data=network1GCfg,
                                  headers=headers,
                                  verify=False)

    testPing(StaticIP1G)

    responsenodeClusterCfg = requests.request("POST",
                                              nurl,
                                              data=nodeClusterCfg,
                                              headers=headers,
                                              verify=False)

    netPortCfg = "{\n\t\"method\": \"GetClusterConfig\"," \
    "\n    \"params\": { },\n    \"id\": 1\n}"
    while buildMipi != 'Bond1G' and buildSipi != 'Bond10G':
        responseBuild = requests.request("POST",
                                         nurl,
                                         data=netPortCfg,
                                         headers=headers,
                                         verify=False)
        buildMipi = (data['result']['cluster']['mipi'])
        buildSipi =( data['result']['cluster']['sipi'])

# Cluster section
finally:
    murl = "https://" + mvipIP + ":443/json-rpc/9.0"    # Mvip based calls

    strap = sfe.get_bootstrap_config()

    while len(strap.nodes) < nodeCount:
        sleep(5)
    nodeArray = str(strap.nodes)

    # Build the cluster config
    clusterBuild = "{\n\t\"method\": \"SetClusterConfig\"," \
                   "\n\t\"params\": {\n\t\t\"cluster\" :{" \
                   "\n\t\t\t\"acceptEula\": True," \
                   "\n\t\t\t\"mvip\": \"" + mvipIP + "\"," \
                   "\n\t\t\t\"svip\": \"" + svipIP + "\"," \
                   "\n\t\t\t\"rep_Count\": \"2\"," \
                   "\n\t\t\t\"username\": \"" + SFUser + "\"," \
                   "\n\t\t\t\"password\": \"" + SFUserPass + "\"," \
                   "\n\t\t\t\"nodes\": \"" + nodeArray + "\"," \
                   "\n    \t\t\t}\n\t\t},\n   \"id\": 1\n}"

    responseClusterBuild = requests.request("POST",
                                            murl,
                                            data=clusterBuild,
                                            headers=headers,
                                            verify=False)

    # Ping MVIP and SVIP before proceeding
    testPing(mvipIP)

    testPing(svipIP)

    # Build array of available drives and add them
    driveArray = [test]
    sfe = ElementFactory.create(mvipIP, SFUser, SFUserPass)
    while len(driveArray) != 0:
        if driveArray[0] = "test":
            driveArray.remove([0])
            list_drives = sfe.list_drives()
            for disk in list_drives.drives:
                if disk.status == "available":
                    driveArray.append(disk.drive_id)
        sfe.add_drives(driveArray)
        sleep(120)

except requests.exceptions.SSLError:
    print("SSL certificate error")
