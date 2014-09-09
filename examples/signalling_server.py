#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq

#import sys, os
#libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..')
#if os.path.isdir(libs_dir):                                       
#    sys.path.append(libs_dir)
import zmqdecorators

SERVICE_NAME="test_signals_rpc"
SERVICE_PORT=6900
SIGNALS_PORT=6901

class myserver(zmqdecorators.service):
    def __init__(self, service_name, service_port):
        super(myserver, self).__init__(service_name, service_port)
        # TODO: other init code ??

    def cleanup(self):
        print("Cleanup called")

    @zmqdecorators.signal(SERVICE_NAME, SIGNALS_PORT)
    def testsignal(self):
        print("Sending testsignal")
        pass

    @zmqdecorators.method()
    def emit_testsignal(self, resp, *args):
        resp.send("ok") # Not required
        self.testsignal()

if __name__ == "__main__":
    instance = myserver(SERVICE_NAME, SERVICE_PORT)
    print("Starting")
    instance.run()
