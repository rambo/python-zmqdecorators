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
service_port=6900 # Set to None for random port

class myserver(object):
    def __init__(self):
        pass

    def run(self):
        print "starting ioloop"
        ioloop.IOLoop.instance().start()

    @zmqdecorators.method(service_name, service_port)
    def beer(self, resp, bottles, drinkers):
        bottles = int(bottles)
        drinkers = int(drinkers)
        print "Sending bottles as reply"
        resp.send("Here's %d bottles of beer for %d drinkers" % (bottles, drinkers))
    
    @zmqdecorators.method(service_name, service_port)
    def food(self, resp, arg, arg2):
        print "Sending noms as reply"
        resp.send("Here's %s for the noms (for %s)" % (arg, arg2))


if __name__ == "__main__":
    instance = myserver()
    instance.run()
