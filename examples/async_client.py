#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq
from zmq.eventloop import ioloop as ioloop_mod
import random
import zmqdecorators

SERVICE_NAME="test_asyncrpc"

class myclient(zmqdecorators.client):
    def __init__(self, myname):
        super(myclient, self).__init__()
        
        self.myname = myname
        self.wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, SERVICE_NAME)
        self.stream = self.wrapper.stream
        self.stream.on_recv(self.client_recv_callback)

        self.pcb = ioloop_mod.PeriodicCallback(self.send_random_data, 100)
        self.pcb.start()

    def client_recv_callback(self, message_parts):
        print "%s: client_recv_callback got %s" % (self.myname, repr(message_parts))

    def send_random_data(self):
        data = "%d" % random.randint(0,100000)
        data2 = "%d" % random.randint(0,10)
        self.wrapper.call("beer", data, data2)
        if random.randint(0,1):
            self.wrapper.call("food", data, data2)
        
if __name__ == "__main__":
    import sys,os
    instance = myclient(sys.argv[1])
    print("Starting")
    instance.run()

