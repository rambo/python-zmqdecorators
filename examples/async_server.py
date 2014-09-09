#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq

#import sys, os
#libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..')
#if os.path.isdir(libs_dir):                                       
#    sys.path.append(libs_dir)
import zmqdecorators

SERVICE_NAME="test_asyncrpc"
SERVICE_PORT=6900 # Set to None for random port

class myserver(zmqdecorators.service):
    def __init__(self, service_name, service_port):
        super(myserver, self).__init__(service_name, service_port)
        # TODO: other init code ??

    def cleanup(self):
        print("Cleanup called")

    @zmqdecorators.method()
    def beer(self, resp, bottles, drinkers):
        bottles = int(bottles)
        drinkers = int(drinkers)
        print "Sending bottles as reply"
        resp.send("Here's %d bottles of beer for %d drinkers" % (bottles, drinkers))

    @zmqdecorators.method()
    def food(self, resp, arg, arg2):
        print "Sending noms as reply"
        resp.send("Here's %s for the noms (for %s)" % (arg, arg2))


if __name__ == "__main__":
    instance = myserver(SERVICE_NAME, SERVICE_PORT)
    print("Starting")
    instance.run()
