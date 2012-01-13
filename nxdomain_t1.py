__author__ = 'liuyang'

def init(id, cfg): return True


def deinit(id): return True


def inform_super(id, qstate, superqstate, qdata): return True


def operate(id, event, qstate, qdata):
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
            #create instance of DNS message (packet) with given parameters
            log_info("pythonmod: type A and Nxdomain")
            msg = DNSMessage(qstate.qinfo.qname_str, RR_TYPE_A, RR_CLASS_IN, PKT_QR | PKT_RA | PKT_AA)
            msg.answer.append("%s 10 IN A 127.0.0.1" % qstate.qinfo.qname_str)
            if not msg.set_return_msg(qstate):
                qstate.ext_state[id] = MODULE_ERROR
                log_error("bad msgset")
                return True
            qstate.return_rcode = RCODE_NOERROR
            #qstate.return_msg.rep.security = 2

    qstate.ext_state[id] = MODULE_FINISHED
    return True
