#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq
import zmqdecorators

SERVICE_NAME="test_asyncrpc"
SERVICE_PORT=6900 # Set to None for random port
SERVICE_PORT=None

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
        # Remember, ZMQ only deals in strings, so typecast everything (JSON is a good idea too)
        resp.send("Here's %d bottles of beer for %d drinkers", str(bottles), str(drinkers))

    @zmqdecorators.method()
    def food(self, resp, arg, arg2):
        print "Sending noms as reply"
        # Remember, ZMQ only deals in strings, so typecast everything (JSON is a good idea too)
        resp.send("Here's %s for the noms (for %s ppl)", str(arg), str(arg2))


if __name__ == "__main__":
    instance = myserver(SERVICE_NAME, SERVICE_PORT)
    print("Starting")
    instance.run()
