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


service_name="test_asyncrpc"

@zmqdecorators.method(service_name)
def beer(bottles):
    bottles = int(bottles)
    print "Sending bottles as reply"
    return "Here's %d bottles of beer" % bottles

@zmqdecorators.method(service_name)
def food(arg):
    print "Sending noms as reply"
    return "Here's %s for the noms" % arg


print "starting ioloop"
ioloop.IOLoop.instance().start()
