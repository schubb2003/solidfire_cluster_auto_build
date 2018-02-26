@@ -1,10 +1,7 @@
 #!/usr/local/bin/python
 # Author: Scott Chubb scott.chubb@netapp.com, Justin Hover justin.hover@netapp.com
-# Date: 8-Jan-2018
-# Version 1.3
-# Notes: This script has been written for python 2.7.14 and 3.6.3
-# on 2.7 you must install requests and ipaddress
-# PEP8 compliance reviewed 7-Dec-2017
+# Date: 25-Jan-2018
+# Version 2.2
 # Script is currently written to read a csv called cvfile for node information
 # It then parses and builds the node information from said csv
 # Format should be as below
@@ -25,9 +22,9 @@
 from solidfire.factory import ElementFactory
 from solidfire.models import *
 
+
 # Function used to determine if the OS is Windows or Unix for testPing
 def testIP(host):
-        loop_count = 0
         if system_name().lower() == "windows":
                 response = os.system("ping -n 2 " + host)
         else:
@@ -36,18 +33,24 @@ def testIP(host):
         while response != 0:
                 print("retrying...")
                 time.sleep(10)
-                loop_count += 1
-                print(loop_count)
-                if loop_count > 10:
-                    sys.exit("Unable to ping node, script has exited")
+                
+# Function to determine if input is a valid IP address, this works for IPv4 and IPv6 
+# This script explicity calls out Python v2 and above as valid and below v2 as unsupported
+# Changes to Python in the future could result in the script needing updated to address said changes                   
+def verifyIP(addr):
+    if sys.version_info[0] == 2:
+        try:
+            verifyIP(addr))
+        except ValueError:
+            sys.exit("Input does not evaluate to an IP address for node %s, submitted IP is %s" % (NodeName,addr))
+    elif sys.version_info[0] > 2:
+        ipaddress.ip_address(addr)
+        except ValueError:
+            sys.exit("Input does not evaluate to an IP address for node %s, submitted IP is %s" % (NodeName,addr))
+    elif sys.version_info[0] < 2:
+        sys.exit("Unsupported version of Python detected, script will exit")
 
-# If not using CSV file, uncomment lines and change length check to 16
-# and swap commenting on Insufficient arguments line
-# Note: the logic does not currently exist to complete build without CSV
 if len(sys.argv) < 6:
-	# print("Insufficient arguments: DHCP|1Gb IP|1Gb netmask|1Gb gateway" + \
-    # "|10Gb IP|10Gb netmask|10Gb gateway|10Gb MTU|DNS server(s)" + \
-    # "|Nodename|Clustername|MVIP IP|User|Password")
     print("Insufficient arguments: Clustername|MVIP IP|SVIP IP|User|Password")
 else:
     # DhcpIP = sys.argv[1]
@@ -65,44 +68,30 @@ def testIP(host):
     SFUser = sys.argv[4]
     SFUserPass = sys.argv[5]
 
-nodeArray = []
-
 try:
-    
-    
-    # Read input file, currently set as CSV for build params
-    with open("csvfile.csv", "rb") as buildFile:
+    nodeArray = []
+    with open("csvfile.csv", "r") as buildFile:
         reader = csv.reader(buildFile, delimiter=",")
         for i, line in enumerate(reader):
+            nodeCount = 1 + i
+            # If using static IPs comment out DhcpIP line and adjust numbering on the remaining lines
             DhcpIP = line[0]
             StaticIP1G = line[1]
             Netmask1G = line[2]
             Gateway1G = line[3]
             NameServer1G = line[4]
             StaticIP10G = line[5]
-            Netmask10G = line[6]
+            MTU10G = line[6]
             NodeName = line[7]
-
     # Verify submissions are valid IP addresses
-    # Warning: this may break on Python versions above 3.x
-            if sys.version_info.major == 2:
-                ipaddress.ip_address(bytearray(DhcpIP))
-                ipaddress.ip_address(bytearray(StaticIP1G))
-                ipaddress.ip_address(bytearray(Netmask1G))
-                ipaddress.ip_address(bytearray(Gateway1G))
-                ipaddress.ip_address(bytearray(NameServer1G))
-                ipaddress.ip_address(bytearray(StaticIP10G))
-                ipaddress.ip_address(bytearray(Netmask10G))
-            elif sys.version_info.major >= 3:
-                ipaddress.ip_address(DhcpIP)
-                ipaddress.ip_address(StaticIP1G)
-                ipaddress.ip_address(Netmask1G)
-                ipaddress.ip_address(Gateway1G)
-                ipaddress.ip_address(NameServer1G)
-                ipaddress.ip_address(StaticIP10G)
-                ipaddress.ip_address(Netmask10G)
-            else:
-                sys.exit("Unsupported Python version")
+            # If using static IPs comment out DhcpIP line and adjust numbering on the remaining lines
+            verifyIP(DhcpIP)
+            verifyIP(StaticIP1G)
+            verifyIP(Netmask1G)
+            verifyIP(Gateway1G)
+            verifyIP(NameServer1G)
+            verifyIP(StaticIP10G)
+            verifyIP(Netmask10G)
 
     # Vars used later
             buildMipi = "" 	# Used in cluster build while loop
@@ -111,39 +100,26 @@ def testIP(host):
     # Print output of submitted information
             print("Configuring cluster: \t" + ClusterName +
                   "\nConfigure via node: \t" + NodeName +
+                  #If using static IPs comment out the DHCP line below
                   "\nConfigure via DHCP: \t" + DhcpIP +
                   "\nConfigure 1G IP: \t" + StaticIP1G +
                   "\nConfigure 1G netmask: \t" + Netmask1G +
                   "\nConfigure 1G gateway: \t" + Gateway1G +
                   "\nConfigure 10G IP: \t" + StaticIP10G +
-                  "\nConfigure 10G netmask: \t" + Netmask10G,
-                  "\n------------------------------------")
+                  "\nConfigure 10G netmask: \t" + Netmask10G)
 
     # Ping the node DHCP address
+            # If using static IPs change DhcpIP to StaticIP1G for both lines below
             testIP(DhcpIP)
-
+            
             sfe = ElementFactory.create(DhcpIP + ":442", "fake", "fake", print_ascii_art="False")
-            if not sfe:
-                # Web/REST auth credentials build authentication
-                auth = ("fake:fake")
-                encodeKey = base64.b64encode(auth.encode('utf-8'))
-                basicAuth = bytes.decode(encodeKey)
-                
-                # Web/REST check for status code
-                url = "https://" + DhcpIP + ":442"  # Node based url
-                requests.request("GET", url, verify_ssl=False)
-                sys.exit("Unable to connect to node:\t %s" % response.status_code)
 
     # Apply configuration to node: 1G, 10G, cluster
-            sfe.set_network_config(network=Network(bond1_g=NetworkConfig(address=StaticIP1G,
-                                                                         netmask=Netmask1G,
-                                                                         gateway=Gateway1G,
-                                                                         dns_nameservers=NameServer1G)))
-            sfe.set_network_config(network=Network(bond10_g=NetworkConfig(address=StaticIP10G,
-                                                                          netmask=Netmask10G,
-                                                                          mtu=MTU10G,
-                                                                          bond_mode="LACP")))
-            sfe.set_cluster_config(cluster=ClusterConfig(name=NodeName, cluster=ClusterName))
+            # If using static IPs comment out the bond1_g line, **NOTE** you may need to configure DNS servers separately
+            sfe.set_network_config(network=Network(bond1_g=NetworkConfig(address=StaticIP1G, netmask=Netmask1G, gateway=Gateway1G, dns_nameservers=NameServer1G)))
+            sfe2 = ElementFactory.create(StaticIP1G + ":442", SFUser, SFUserPass, print_ascii_art="false")
+            sfe2.set_network_config(network=Network(bond10_g=NetworkConfig(address=StaticIP10G, netmask=Netmask10G, mtu=MTU10G, bond_mode="LACP")))
+            sfe2.set_cluster_config(cluster=ClusterConfig(name=NodeName, cluster=ClusterName))
 
     # Place 10G IP in array for later cluster creation
             nodeArray.append(StaticIP10G)
@@ -155,37 +131,26 @@ def testIP(host):
 
 # Cluster section
 finally:
-
-    sfe = ElementFactory.create(StaticIP1G,
-                                SFUser,
-                                SFUserPass,
-                                print_ascii_art="False")
-
+    time.sleep(30)
+    sfe3 = ElementFactory.create(StaticIP1G, SFUser, SFUserPass)
+    sfe3.timeout(300)
     # Build the cluster config
 
-    sfe.create_cluster(mvip=mvipIP,
-                       svip=svipIP,
-                       username=SFUser,
-                       password=SFUserPass,
-                       nodes=nodeArray,
-                       rep_count=2,
-                       accept_eula="True")
-
-    print "Creating cluster " + ClusterName
-    time.sleep(300)
+    sfe3.create_cluster(mvip=mvipIP, svip=svipIP, username=SFUser, password=SFUserPass, nodes=nodeArray, rep_count=2, accept_eula="true")
+    print("Creating cluster " + ClusterName)
 
     # Ping MVIP before proceeding
     testIP(mvipIP)
 
     # Build array of available drives and add them
     driveArray = []
-    sfe = ElementFactory.create(mvipIP, SFUser, SFUserPass, print_ascii_art="False")
+    sfe4 = ElementFactory.create(mvipIP, SFUser, SFUserPass, print_ascii_art="false")
     list_drives = sfe.list_drives()
     for disk in list_drives.drives:
         if disk.status == "available":
             driveArray.append(disk.drive_id)
-    sfe.add_drives(driveArray)
-    print "Adding all available drives..."
+    sfe4.add_drives(driveArray)
+    print("Adding all available drives...")
     time.sleep(60)
 
-    print "Cluster Configuration Complete"
+    print("Cluster Configuration Complete")