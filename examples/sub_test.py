#!/usr/bin/env python
import zmq
from zmq.eventloop import ioloop
ioloop.install()

#import sys, os
#libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..', 'zmqdecorators')
#if os.path.isdir(libs_dir):                                       
#    sys.path.append(libs_dir)
import zmqdecorators


def bottles_callback(data):
    """Since we know the exact amount and order of arguments we can get away with not adding *args. Whether adding it to avoid choking in case for channel
    format changes is a good idea depends on your circumstances (sometimes it's better to catch the change early"""
    print "in bottles_callback got %s" % repr(data)

def slices_callback(data):
    print "in slices_callback got %s" % repr(data)

def all_callback(*args):
    """The generic callback MUST accept any number of arguments (including zero)"""
    print "in all_callback got %s" % repr(args)

zmqdecorators.subscribe_topic("test_pubsub", "bottles", bottles_callback)
zmqdecorators.subscribe_topic("test_pubsub", "slices", slices_callback)
zmqdecorators.subscribe_all("test_pubsub", all_callback)


print "starting ioloop"
ioloop.IOLoop.instance().start()

