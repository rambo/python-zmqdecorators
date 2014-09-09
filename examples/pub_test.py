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


SERVICE_NAME="test_pubsub"
SIGNALS_PORT=5555 # Set to None for random port


class mypublisher(zmqdecorators.service):

    def __init__(self, service_name):
        super(mypublisher, self).__init__(service_name)

        self.pcb = ioloop_mod.PeriodicCallback(self.bottles_caller, 500)
        self.pcb.start()
        self.pcb2 = ioloop_mod.PeriodicCallback(self.slices_caller, 500)
        self.pcb2.start()

        self.pcb3 = ioloop_mod.PeriodicCallback(self.noargs, 500)
        self.pcb3.start()


    @zmqdecorators.signal(SERVICE_NAME, SIGNALS_PORT)
    def noargs(self, *args):
        """What this function actually does, does not matter to the ZMQ PUBlish, the function name is the topic and function arguments rest of the message parts"""
        print "No args signal called"
        pass

    @zmqdecorators.signal(SERVICE_NAME, SIGNALS_PORT)
    def bottles(self, n):
        """What this function actually does, does not matter to the ZMQ PUBlish, the function name is the topic and function arguments rest of the message parts"""
        pass

    def bottles_caller(self):
        """We call this function from the eventloop so we have a nice random argument to pass to the bottles-signal"""
        n = random.randint(0,100000)
        data = "%s bottles of beer on the wall" % n
        print data
        return self.bottles(data)

    @zmqdecorators.signal(SERVICE_NAME, SIGNALS_PORT)
    def slices(self, n):
        pass

    def slices_caller(self):
        n = random.randint(0,100000)
        data = "%s slices in the box" % n
        print data
        return self.slices(data)



if __name__ == "__main__":
    instance = mypublisher(SERVICE_NAME)
    print("Starting")
    instance.run()

