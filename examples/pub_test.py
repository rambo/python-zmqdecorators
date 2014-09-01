#!/usr/bin/env python
import zmq
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream
ioloop.install()

#import sys, os
#libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..')
#if os.path.isdir(libs_dir):                                       
#    sys.path.append(libs_dir)
import zmqdecorators

import itertools
import random

service_name="test_pubsub"
service_port=5555 # Set to None for random port

@zmqdecorators.signal(service_name, service_port)
def bottles(n):
    """What this function actually does, does not matter to the ZMQ PUBlish, the function name is the topic and function arguments rest of the message parts"""
    pass

def bottles_caller():
    """We call this function from the eventloop so we have a nice random argument to pass to the bottles-signal"""
    n = random.randint(0,100000)
    data = "%s bottles of beer on the wall" % n
    print data
    return bottles(data)

@zmqdecorators.signal(service_name, service_port)
def slices(n):
    pass

def slices_caller():
    n = random.randint(0,100000)
    data = "%s slices in the box" % n
    print data
    return slices(data)


pcb = ioloop.PeriodicCallback(bottles_caller, 100)
pcb.start()
pcb2 = ioloop.PeriodicCallback(slices_caller, 100)
pcb2.start()

print "starting ioloop"
ioloop.IOLoop.instance().start()
