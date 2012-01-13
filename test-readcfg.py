#-*- coding: utf-8 -*-

__author__ = 'liuyang'

excludeIpCfg="eip.cfg"
excludeNameCfg="exname.cfg"
rewriteIpCfg="rip.cfg"

import os.path
import netaddr

myExIpCfg = ""
myRwIpCfg = ""
myExNameCfg = ""

cfgPath=[r'./', r'/etc/', r'/etc/unbound/']

class RewriteIP:
    def __init__(self):
        self.ips = []
        self.index = 0

    def add(self, ip):
        self.ips.append(ip)

    def getIp(self):
        if self.ips:
            if 1 == len(self.ips):
                return self.ips[0]
            if self.index >= len(self.ips):
                self.index=1
                return self.ips[0]
            else:
                cur=self.index
                self.index += 1
                return self.ips[cur]
        else:
            return "127.0.0.1"

    def __str__(self):
        string=""
        for ip in self.ips:
            string += ip + "\n"
        return string

class ExcludeIP:
    def __init__(self):
        self.cidrs = []

    def add(self, cidr):
        self.cidrs.append(cidr)

    def isin(self,ip):
        if not self.cidrs:
            return False
        if netaddr.all_matching_cidrs(ip, self.cidrs):
            return True
        else:
            return False

    def __str__(self):
        string=""
        for cidr in self.cidrs:
            string += cidr + "\n"
        return string

class ExcludeName:
    def __init__(self):
        self.names = []

    def add(self, name):
        self.names.append(name)

    def ismatch(self, name):
        if not self.names:
            return False
        for ename in self.names:
            if -1 != name.rfind(ename):
                return True

        return False

    def __str__(self):
        string=""
        for name in self.names:
            string += name + "\n"
        return string

mExIp=ExcludeIP()
mExName=ExcludeName()
mRwIp=RewriteIP()


#初始化部分

#不转发IP设置
for path in cfgPath:
    if os.path.isfile(path+excludeIpCfg):
        myExIpCfg = path + excludeIpCfg
        break
if len(myExIpCfg):
    print "exclude ip config file is " + myExIpCfg
    f = open(myExIpCfg, "r")
    try:
        for line in f:
            mExIp.add(line.strip())
    finally:
        f.close()
        print mExIp
else:
    print "no exclude ip config file found!"


#转发目标IP设置
for path in cfgPath:
    if os.path.isfile(path+rewriteIpCfg):
        myRwIpCfg = path + rewriteIpCfg
        break
if len(myRwIpCfg):
    print "rewrite ip config file is " + myRwIpCfg
    f = open(myRwIpCfg, "r")
    try:
        for line in f:
            mRwIp.add(line.strip())
    finally:
        f.close()
        print mRwIp
else:
    print "no rewrite ip config file found!"

#不转发域名部分
for path in cfgPath:
    if os.path.isfile(path+excludeNameCfg):
        myExNameCfg = path + excludeNameCfg
        break
if len(myExNameCfg):
    print "exclude name config file is " + myExNameCfg
    f = open(myExNameCfg, "r")
    try:
        for line in f:
            mExName.add(line.strip())
    finally:
        f.close()
        print mExName
else:
    print "no exclude name config file found!"



#testing

print mExName.ismatch("www.sina.com")
print mExName.ismatch("www.sohu.com")
print mExName.ismatch("2012.www.yahoo.com")
print mExName.ismatch("www.sina.com.cn")
print mExName.ismatch("www.sina.cn")
print "========================================="
print mExIp.isin("192.168.0.1")
print mExIp.isin("192.168.0.128")
print mExIp.isin("10.10.10.10")
print mExIp.isin("202.123.53.12")
print "========================================="
for i in range(10):
    print mRwIp.getIp()
