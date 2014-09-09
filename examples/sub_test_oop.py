#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq
from zmq.eventloop import ioloop as ioloop_mod

#import sys, os
#libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..', 'zmqdecorators')
#if os.path.isdir(libs_dir):                                       
#    sys.path.append(libs_dir)
import zmqdecorators

class mysubscriber(zmqdecorators.client):
    def __init__(self):
        super(mysubscriber, self).__init__()

        zmqdecorators.subscribe_topic("test_pubsub", "bottles", self.bottles_callback)
        zmqdecorators.subscribe_topic("test_pubsub", "slices", self.slices_callback)
        zmqdecorators.subscribe_topic("test_pubsub", "noargs", self.noargs_callback)
        zmqdecorators.subscribe_all("test_pubsub", self.all_callback)

    def bottles_callback(self, data):
        """Since we know the exact amount and order of arguments we can get away with not adding *args. Whether adding it to avoid choking in case for channel
        format changes is a good idea depends on your circumstances (sometimes it's better to catch the change early"""
        print "in bottles_callback got %s" % repr(data)

    def slices_callback(self, data):
        print "in slices_callback got %s" % repr(data)

    def noargs_callback(self):
        print "in noargs_callback"

    def all_callback(self, *args):
        """The generic callback MUST accept any number of arguments (including zero)"""
        print "in all_callback got %s" % repr(args)


if __name__ == "__main__":
    instance = mysubscriber()
    print("Starting")
    instance.run()
