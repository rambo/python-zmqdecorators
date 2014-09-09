#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities and decorators for PyZMQ, emulating the way python-dbus decorators work (which make things super-easy for the developer)"""
import zmq
from zmq.eventloop import ioloop
ioloop.install()
from zmq.eventloop.zmqstream import ZMQStream
import time
import uuid
import functools
import bonjour_utilities
from exceptions import RuntimeError,KeyboardInterrupt
import signal as posixsignal


def socket_type_to_service(socket_type):
    if socket_type == zmq.PUB:
        return "_zmqpubsub._tcp."
    if socket_type == zmq.SUB:
        return "_zmqpubsub._tcp."

    if socket_type == zmq.ROUTER:
        return "_zmqdealerrouter._tcp."
    if socket_type == zmq.DEALER:
        return "_zmqdealerrouter._tcp."

    # TODO: Implement more types
    # TODO: Raise error for unknown types


class zmq_client_response(object):
    client_id = None
    stream = None
    
    def __init__(self, client_id, stream):
        self.stream = stream
        self.client_id = client_id
    
    def send(self, *args):
        self.stream.send_multipart([self.client_id, ] + list(args))

class zmq_bonjour_bind_base(object):
    """Binds to a ZMQ socket by the name"""
    context = None
    socket = None
    stream = None
    heartbeat_timer = None
    port = None
    bonjour_registration = None

    def _hearbeat(self):
        #print "Sending heartbeat"
        self.stream.send_multipart(("HEARTBEAT", "1"))

    def __init__(self, socket_type, service_name, service_port=None, service_type=None):
        self.context = zmq.Context()
        self.socket = self.context.socket(socket_type)
        if not service_port:
            service_port = self.socket.bind_to_random_port('tcp://*', min_port=49152, max_port=65535, max_tries=100)
        else:
            self.socket.bind("tcp://*:%d" % service_port)
        #print "Bound to port %d" % service_port
        self.port = service_port

        self.stream = ZMQStream(self.socket)
        if not service_type:
            service_type = socket_type_to_service(socket_type)

        if socket_type == zmq.PUB:
            # TODO: how to handle this with ROUTER/DEALER combinations...
            self.heartbeat_timer = ioloop.PeriodicCallback(self._hearbeat, 1000)
            self.heartbeat_timer.start()

        self.bonjour_registration = bonjour_utilities.register_ioloop(ioloop.IOLoop.instance(), service_type, service_name, service_port)


class zmq_bonjour_bind_wrapper(zmq_bonjour_bind_base):
    """Binds to a ZMQ socket by the name, handles callbacks for decorated simple functions"""
    method_callbacks = {}

    def __init__(self, socket_type, service_name, service_port=None, service_type=None):
        super(zmq_bonjour_bind_wrapper, self).__init__(socket_type, service_name, service_port, service_type)

        if socket_type == zmq.ROUTER:
            self.stream.on_recv(self._method_callback_wrapper)

    def _method_callback_wrapper(self, datalist):
        #print "_method_callback_wrapper called: %s" % repr(datalist)
        if len(datalist) < 2:
            return
        client_id = datalist[0]
        method = datalist[1]
        args = datalist[2:]
        #print "DEBUG: _method_callback_wrapper(%s, %s)" % (method, repr(args))
        if not self.method_callbacks.has_key(method):
            raise RuntimeError("No such method: %s" % method)
            #print "No such method: %s" % method
            #print "Methods: %s" % self.method_callbacks.keys()
            return
        for f in self.method_callbacks[method]:
            resp = zmq_client_response(client_id, self.stream)
            # TODO: make a wrapper object for sending responses and pass that instead of the client_id
            #print "Calling f(resp, %s)" % repr(args)
            f(resp, *args)

    def register_method(self, name, callback):
        if not self.method_callbacks.has_key(name):
            self.method_callbacks[name] = []
        self.method_callbacks[name].append(callback)


class service_baseclass(zmq_bonjour_bind_base):
    """Baseclass for services in ZMQ with RPC methods"""
    def __init__(self, service_name, service_port=None, service_type=None, ioloop_instance=None):
        super(service_baseclass, self).__init__(zmq.ROUTER, service_name, service_port, service_type)
        self.stream.on_recv(self._method_callback_wrapper)
        if ioloop_instance:
            self.ioloop = ioloop_instance
        else:
            self.ioloop = ioloop.IOLoop.instance()

    def _method_callback_wrapper(self, datalist):
        if len(datalist) < 2:
            # Invalid call (no client-id and no method name)
            return
        client_id = datalist[0]
        method = datalist[1]
        args = datalist[2:]
        
        try:
            f = getattr(self, method)
            #print("f.__dict__\n==\n%s\n===\n" % repr(f.__dict__))
            if not '_method__zmqdecorators_is_method' in f.__dict__:
                raise RuntimeError("No such method: %s" % method)
            resp = zmq_client_response(client_id, self.stream)
            f(resp, *args)

        except AttributeError,e:
            raise RuntimeError("No such method: %s" % method)

    def hook_signals(self):
        """Hooks common UNIX signals to corresponding handlers"""
        posixsignal.signal(posixsignal.SIGTERM, self.quit)
        posixsignal.signal(posixsignal.SIGQUIT, self.quit)
        posixsignal.signal(posixsignal.SIGHUP, self.reload)

    def reload(self):
        """Overload this method if you want to handle SIGHUP"""
        pass

    def cleanup(self):
        """Overload this method if you need to do cleanups (though atexit would probably be better"""
        pass

    def quit(self):
        """Quits the IOLoop"""
        self.ioloop.stop()

    def run(self):
        """Starts the IOLoop"""
        self.hook_signals()
        try:
            self.ioloop.start()
        except KeyboardInterrupt:
            self.quit()
        finally:
            self.cleanup()


class zmq_bonjour_connect_wrapper(object):
    """Connects to a ZMQ socket by the name, handles callbacks for pubsub topics etc"""
    context = None
    socket = None
    stream = None
    heartbeat_received = None
    heartbeat_timeout = 5000
    topic_callbacks = {}
    recv_callbacks = []
    uuid = None
    identity = None

    def __init__(self, socket_type, service_name, service_port=None, service_type=None, identity=None):
        self.uuid = uuid.uuid4()
        if not identity:
            self.identity = self.uuid.hex
        else:
            self.identity = identity

        self.reconnect(socket_type, service_name, service_port=None, service_type=None)
        if socket_type == zmq.SUB:
            # TODO: how to handle this with ROUTER/DEALER combinations...
            self.add_topic_callback("HEARTBEAT", self._heartbeat_callback)
            # TODO: add heartbeat watcher callback

    def _heartbeat_callback(self, *args):
        self.heartbeat_received = time.time()
        #print "Heartbeat time %d" % self.heartbeat_received

    def _topic_callback_wrapper(self, datalist):
        for f in self.recv_callbacks:
            f(*datalist)
        topic = datalist[0]
        args = datalist[1:]
        #print "DEBUG: _topic_callback_wrapper(%s, %s)" % (topic, repr(args))
        if not self.topic_callbacks.has_key(topic):
            return
        for f in self.topic_callbacks[topic]:
            f(*args)

    def reconnect(self, socket_type, service_name, service_port=None, service_type=None):
        self.context = None
        self.socket = None
        self.stream = None
        self.heartbeat_received = None

        if not service_type:
            service_type = socket_type_to_service(socket_type)
        if isinstance(service_name, (list, tuple)):
            rr = [None, service_name[0], service_name[1]]
        else:
            rr = bonjour_utilities.resolve(service_type, service_name)
        if not rr:
            # TODO raise error or wait ??
            return

        self.context = zmq.Context()
        self.socket = self.context.socket(socket_type)
        self.socket.setsockopt(zmq.IDENTITY, self.identity)
        self.stream = ZMQStream(self.socket)
        connection_str =  "tcp://%s:%s" % (rr[1], rr[2])
        self.socket.connect(connection_str)

        # re-register the subscriptions
        for topic in self.topic_callbacks.keys():
            self._subscribe_topic(topic)

        # And set the callback
        self.stream.on_recv(self._topic_callback_wrapper)

    def _subscribe_topic(self, topic):
        self.socket.setsockopt(zmq.SUBSCRIBE, topic)

    def add_recv_callback(self, callback):
        self.recv_callbacks.append(callback)        

    def add_topic_callback(self, topic, callback):
        if not self.topic_callbacks.has_key(topic):
            self.topic_callbacks[topic] = []
            self._subscribe_topic(topic)
        self.topic_callbacks[topic].append(callback)

    def call(self, method, *args):
        """Async method calling wrapper, does not return anything you will need to catch any responses the server might send some other way"""
        self.stream.send_multipart([method, ] + list(args))


class client_baseclass(object):
    """Baseclass for clients, basically just handles some basic housekeeping like signals etc"""
    def __init__(self, ioloop_instance=None):
        if ioloop_instance:
            self.ioloop = ioloop_instance
        else:
            self.ioloop = ioloop.IOLoop.instance()

    def hook_signals(self):
        """Hooks common UNIX signals to corresponding handlers"""
        posixsignal.signal(posixsignal.SIGTERM, self.quit)
        posixsignal.signal(posixsignal.SIGQUIT, self.quit)
        posixsignal.signal(posixsignal.SIGHUP, self.reload)

    def reload(self):
        """Overload this method if you want to handle SIGHUP"""
        pass

    def cleanup(self):
        """Overload this method if you need to do cleanups (though atexit would probably be better"""
        pass

    def quit(self):
        """Quits the IOLoop"""
        self.ioloop.stop()

    def run(self):
        """Starts the IOLoop"""
        self.hook_signals()
        try:
            self.ioloop.start()
        except KeyboardInterrupt:
            self.quit()
        finally:
            self.cleanup()


class server_tracker(object):
    """Used to keep track of bound services by their names"""
    by_names = {}

    def __init__(self):
        pass

    def get_by_name(self, service_name, socket_type):
        service_type = socket_type_to_service(socket_type)
        key = "%s%s" % (service_name, service_type)
        if self.by_names.has_key(key):
            return self.by_names[key]
        return None

    def create(self, service_name, socket_type, port=None):
        service_type = socket_type_to_service(socket_type)
        key = "%s%s" % (service_name, service_type)
        self.by_names[key] = zmq_bonjour_bind_wrapper(socket_type, service_name, port)
        return self.by_names[key]

    def get_by_name_or_create(self, service_name, socket_type, port=None):
        r = self.get_by_name(service_name, socket_type)
        if not r:
            r = self.create(service_name, socket_type, port)
        if port:
            if not port == r.port:
                raise RuntimeError("Tried to bind name %s to port %d but it has already been bound to %d" % (service_name, port, r.port))
        return r

dt = server_tracker()

class signal(object):
    """This exposes the decorated function as a PUB/SUB published signal, topic is the method name and any arguments for the method are passed on as data"""
    wrapper = None
    stream = None

    def __init__(self, service_name, port=None):
        self.wrapper = dt.get_by_name_or_create(service_name, zmq.PUB, port=None)
        self.stream = self.wrapper.stream

    def __call__(self, f):
        def wrapped_f(*args):
            topic = f.__name__
            # This signal is a class method
            if (    len(args) >= 1
                and isinstance(args[0], service_baseclass)):
                self.stream.send_multipart([topic, ] + list(args[1:]))
            else:
                self.stream.send_multipart([topic, ] + list(args))
            f(*args)
        return wrapped_f


class method(object):
    """This exposes the decorated function as async RPC method, use the passed client_response instance to send data back, note: unless that data (and the request params) contain some transaction id client cannot be sure which call a response corresponds to"""
    wrapper = None
    stream = None

    def __init__(self, service_name=None, port=None):
        if service_name:
            # This is the case for simple functions decorated where we need to create a wrapper class to track them
            self.wrapper = dt.get_by_name_or_create(service_name, zmq.ROUTER, port)
            self.stream = self.wrapper.stream

    def __call__(self, f):
        if self.wrapper:
            # This is the case for simle functions
            method = f.__name__
            def wrapped_f(*args):
                f(*args)
            self.wrapper.register_method(method, wrapped_f)
            return wrapped_f
        else:
            # And this for class methods
            f.__zmqdecorators_is_method = True
            return f



class client_tracker(object):
    """Used to keep track of connections to services by their names"""
    by_names = {}

    def __init__(self):
        pass

    def _by_name_key(self, service_name, socket_type):
        service_type = socket_type_to_service(socket_type)
        if isinstance(service_name, (list, tuple)):
            key = "ip(%s:%s)/%s" % (service_name[0], service_name[1], service_type)
        else:
            key = "%s/%s" % (service_name, service_type)
        return key

    def get_by_name(self, service_name, socket_type):
        key = self._by_name_key(service_name, socket_type)
        if self.by_names.has_key(key):
            return self.by_names[key]
        return None

    def create(self, service_name, socket_type):
        key = self._by_name_key(service_name, socket_type)
        self.by_names[key] = zmq_bonjour_connect_wrapper(socket_type, service_name)
        return self.by_names[key]

    def get_by_name_or_create(self, service_name, socket_type):
        r = self.get_by_name(service_name, socket_type)
        if not r:
            r = self.create(service_name, socket_type)
        return r

ct = client_tracker()


def call(service_name, method, *args):
    """Async method calling wrapper, does not return anything you will need to catch any responses the server might send some other way"""
    if isinstance(service_name, zmq_bonjour_connect_wrapper):
        wrapper = service_name
    else:
        wrapper = ct.get_by_name_or_create(service_name, zmq.DEALER)
    wrapper.call(method, *args)
    

class sync_return_wrapper():
    return_value = None
    ready = False

    def callback(self, *args):
        self.return_value = args
        self.ready = True
        ioloop.IOLoop.instance().stop()


def call_sync(service_name, method, *args):
    """Sync method calling, will block untill a response matching this request is received. NOTE: Never use this if you use the ioloop for something (since this will play merry hell with starting and stopping the ioloop)"""
    if isinstance(service_name, zmq_bonjour_connect_wrapper):
        stream_wrapper = service_name
    else:
        stream_wrapper = ct.get_by_name_or_create(service_name, zmq.DEALER)
    cb_wrapper = sync_return_wrapper()
    stream_wrapper.stream.on_recv(cb_wrapper.callback)
    call(service_name, method, *args)
    ioloop.IOLoop.instance().start()
    return cb_wrapper.return_value


def subscribe_topic(service_name, topic, callback):
    """Subscribes to the given topic on the given service name (which must be of type zmq.PUB)"""
    if isinstance(service_name, zmq_bonjour_connect_wrapper):
        wrapper = service_name
    else:
        wrapper = ct.get_by_name_or_create(service_name, zmq.SUB)
    wrapper.add_topic_callback(topic, callback)


def subscribe_all(service_name, callback):
    """Subscribes to the given topic on the given service name (which must be of type zmq.PUB) NOTE: this callback must accept any number of arguments!"""
    if isinstance(service_name, zmq_bonjour_connect_wrapper):
        wrapper = service_name
    else:
        wrapper = ct.get_by_name_or_create(service_name, zmq.SUB)
    wrapper.add_recv_callback(callback)

