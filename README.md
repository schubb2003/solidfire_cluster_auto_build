# solidfire_cluster_auto_build
build a SolidFire cluster from RTFI'd nodes via python

This script helps show how to build a NetApp SolidFire cluster from the point of having RTFI'd nodes available via DHCP.

# Script is currently written to read a csv called csvfile for information
# It then parses and builds the node information from said csv
# Format should be as below
# dhcpIP(if used),1Gb_IP,1G_mask,1g_gateway,1G_DNSservers,
#   10Gb_IP,10G_mask,10G_MTU,nodeName
# Script expects arguments for cluster build information
# Args are as follows:
# Clustername,MVIP,SVIP,cluster admin, cluster admin password (change DHCP IPs |don't change) (converge managment IPs | don't converge)
# Usage: python build.py -cn sfdemo1 -m 192.168.0.101 -s 192.168.0.130 -u admin -p Netapp1! (-d | -nd) (-c | -nc)

-cn 
  clustername
-mv
  MVIP IP
-sv
  SVIP IP
-un
  Cluster admin username
-pw 
  Cluster admin password
-ud
  Set to update DHCP IPs on the 1GbE network
-nd
  Set to ignore existing static IPs configured on 1GbE
-cm
  Set to enable convergence of management onto 10GbE storage network ports
-nc
  Set to disable convergence of management and use 1GbE network ports
