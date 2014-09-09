#!/usr/bin/env python
# -*- coding: utf-8 -*-
import zmq
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream
ioloop.install()
import itertools
import random
import time

#import sys, os
#libs_dir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),  '..')
#if os.path.isdir(libs_dir):                                       
#    sys.path.append(libs_dir)
import zmqdecorators

service_name="test_asyncrpc"


data = "%d" % random.randint(0,100000)
data2 = "%d" % random.randint(0,10)
resp = zmqdecorators.call_sync(service_name, "beer", data, data2)
print "got %s" % (repr(resp))


