__author__ = 'liuyang'
import netaddr

ip1=netaddr.IPNetwork('192.168.0.1')

cidr1=['192.168.0/24']
cidr2=['192.168.1/24']

r1 = netaddr.all_matching_cidrs(ip1, cidr1)
r2 = netaddr.all_matching_cidrs(ip1, cidr2)

if(r2 == []):
    print "not in cidr2"
if(r1 == []):
    print "not in cidr1"
