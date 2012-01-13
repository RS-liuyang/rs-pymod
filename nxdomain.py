#-*- coding: utf-8 -*-
__author__ = 'liuyang'

import os.path
import sys

sys.path.append("/usr/local/lib/python2.6/dist-packages/netaddr-0.7.6-py2.6.egg")

import netaddr

excludeIpCfg="eip.cfg"
excludeNameCfg="exname.cfg"
rewriteIpCfg="rip.cfg"

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

    def isup(self):
        if not self.cidrs:
            return False
        return True

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


def init(id, cfg):
    myExIpCfg = ""
    myRwIpCfg = ""
    myExNameCfg = ""

    for path in cfgPath:
        if os.path.isfile(path+excludeIpCfg):
            myExIpCfg = path + excludeIpCfg
            break

    if len(myExIpCfg):
        log_info("exclude ip config file is " + myExIpCfg)
        f = open(myExIpCfg, "r")
        try:
            for line in f:
                mExIp.add(line.strip())
        finally:
            f.close()

            log_info(mExIp.__str__())
    else:
        log_info("no exclude ip config file found!")

    #转发目标IP设置
    for path in cfgPath:
        if os.path.isfile(path+rewriteIpCfg):
            myRwIpCfg = path + rewriteIpCfg
            break
    if len(myRwIpCfg):
        log_info("rewrite ip config file is " + myRwIpCfg)
        f = open(myRwIpCfg, "r")
        try:
            for line in f:
                mRwIp.add(line.strip())
        finally:
            f.close()
            log_info(mRwIp.__str__())
    else:
        log_info("no rewrite ip config file found!")

    #不转发域名部分
    for path in cfgPath:
        if os.path.isfile(path+excludeNameCfg):
            myExNameCfg = path + excludeNameCfg
            break
    if len(myExNameCfg):
        log_info("exclude name config file is " + myExNameCfg)
        f = open(myExNameCfg, "r")
        try:
            for line in f:
                mExName.add(line.strip())
        finally:
            f.close()
            log_info(mExName.__str__())
    else:
        log_info("no exclude name config file found!")

    return True


def deinit(id): return True


def inform_super(id, qstate, superqstate, qdata): return True


def operate(id, event, qstate, qdata):
    ttl = 60
    if (event == MODULE_EVENT_NEW) or (event == MODULE_EVENT_PASS):
        #pass the query to the next module
        qstate.ext_state[id] = MODULE_WAIT_MODULE
        return True

    if event == MODULE_EVENT_MODDONE:
        log_info("pythonmod: iterator module done")

        if not qstate.return_msg:
            qstate.ext_state[id] = MODULE_FINISHED
            return True

        log_info("pythonmod: begin modify the response type is %d, rcode is %d"\
        %(qstate.qinfo.qtype, (qstate.return_msg.rep.flags & 0xf)))
        #modify the response
        if (qstate.qinfo.qtype == RR_TYPE_A) and ((qstate.return_msg.rep.flags & 0xf)==3):
            if mExName.ismatch(qstate.qinfo.qname_str):
                qstate.ext_state[id] = MODULE_FINISHED
                return True

            if mExIp.isup() and qstate.mesh_info.reply_list and qstate.mesh_info.reply_list.query_reply:
                if mExIp.isin(qstate.mesh_info.reply_list.query_reply.addr):
                    qstate.ext_state[id] = MODULE_FINISHED
                    return True
                else:
                    ttl = 0

            #create instance of DNS message (packet) with given parameters
            log_info("pythonmod: type A and Nxdomain")
            msg = DNSMessage(qstate.qinfo.qname_str, RR_TYPE_A, RR_CLASS_IN, PKT_QR | PKT_RA | PKT_AA)

            msg.answer.append("%s %d IN A %s" % (qstate.qinfo.qname_str, ttl, mRwIp.getIp()))
            if not msg.set_return_msg(qstate):
                qstate.ext_state[id] = MODULE_ERROR
                log_err("bad msgset")
                return True
            qstate.return_rcode = RCODE_NOERROR
            #qstate.return_msg.rep.security = 2

    qstate.ext_state[id] = MODULE_FINISHED
    return True
