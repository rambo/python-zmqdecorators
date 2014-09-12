#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq
from zmq.eventloop import ioloop
ioloop.install()
import itertools
import random

import sys
myname = sys.argv[1]

#import sys, os
#libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..')
#if os.path.isdir(libs_dir):                                       
#    sys.path.append(libs_dir)
import zmqdecorators

service_name="test_asyncrpc"

#wrapper = zmqdecorators.ct.get_by_name_or_create(service_name, zmq.DEALER)
wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.DEALER, service_name)

stream = wrapper.stream

def client_recv_callback(message_parts):
    print "%s: client_recv_callback got %s" % (myname, repr(message_parts))

stream.on_recv(client_recv_callback)

def send_random_data():
    data = "%d" % random.randint(0,100000)
    data2 = "%d" % random.randint(0,10)
    #zmqdecorators.call(service_name, "beer", data)
    zmqdecorators.call(wrapper, "beer", data, data2)
    if random.randint(0,1):
        #zmqdecorators.call(service_name, "food", data)
        zmqdecorators.call(wrapper, "food", data, data2)
        

pcb = ioloop.PeriodicCallback(send_random_data, 100)
pcb.start()


print "starting ioloop"
ioloop.IOLoop.instance().start()
