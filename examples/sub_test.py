#!/usr/bin/env python
import zmq
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream
ioloop.install()

#import sys, os
#libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..', 'zmqdecorators')
#if os.path.isdir(libs_dir):                                       
#    sys.path.append(libs_dir)
import zmqdecorators


wrapper = zmqdecorators.zmq_bonjour_connect_wrapper(zmq.SUB, "test_pubsub")

def bottles_callback(data):
    print "in bottles_callback got %s" % repr(data)

def slices_callback(data):
    print "in slices_callback got %s" % repr(data)

wrapper.add_topic_callback("bottles", bottles_callback)
wrapper.add_topic_callback("slices", slices_callback)

print "starting ioloop"
ioloop.IOLoop.instance().start()

