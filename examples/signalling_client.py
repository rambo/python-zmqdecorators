#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq
from zmq.eventloop import ioloop as ioloop_mod
import random

#import sys, os
#libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..')
#if os.path.isdir(libs_dir):                                       
#    sys.path.append(libs_dir)
import zmqdecorators

SERVICE_NAME="test_signals_rpc"


class myclient(zmqdecorators.client):
    def __init__(self):
        super(myclient, self).__init__()
        
        zmqdecorators.subscribe_topic(SERVICE_NAME, 'testsignal', self.testsignal_callback)
        self.wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, SERVICE_NAME)

        self.pcb = ioloop_mod.PeriodicCallback(self.request_testsignal, 500)
        self.pcb.start()

    def testsignal_callback(self, *args):
        print "Got testsignal: %s" % repr(args)

    def request_testsignal(self):
        print("Requesting testsignal")
        self.wrapper.call("emit_testsignal")
        
if __name__ == "__main__":
    instance = myclient()
    print("Starting")
    instance.run()

