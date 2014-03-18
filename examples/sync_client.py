#!/usr/bin/env python
import zmq
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream
ioloop.install()
import itertools
import random
import time

import sys

import sys, os
libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..', 'lib')
if os.path.isdir(libs_dir):                                       
    sys.path.append(libs_dir)
import zmq_utilities

service_name="test_asyncrpc"


while(True):
    data = "%d" % random.randint(0,100000)
    resp = zmq_utilities.call_sync(service_name, "beer", data)
    print "got %s" % (repr(args))
    time.sleep(0.100)

