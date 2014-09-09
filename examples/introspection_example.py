#!/usr/bin/env python
# -*- coding: utf-8 -*-

class decorator(object):
    def __init__(self, arg1):
        self.arg1 = arg1


    def __call__(self, f):
        f.__decorator_arg1 = self.arg1
        return f


class myclass(object):
    def __init__(self):
        pass
    
    def method1(self, arg1):
        pass

    @decorator('foobar')
    def method2(self, arg1):
        pass



i = myclass()

# copied from dbus bindings
print "i.__class__.__mro__[0].__dict__\n==\n%s\n===\n" % repr(i.__class__.__mro__[0].__dict__)
print "i.__class__.__mro__[0].__dict__['method1'].__dict__\n==\n%s\n===\n" % repr(i.__class__.__mro__[0].__dict__['method1'].__dict__)
print "i.__class__.__mro__[0].__dict__['method2'].__dict__\n==\n%s\n===\n" % repr(i.__class__.__mro__[0].__dict__['method2'].__dict__)

m2 = getattr(i, 'method2')
print("m2.__dict__\n==\n%s\n===\n" % repr(m2.__dict__))

v = getattr(m2, '__decorator_arg1')
print repr(v)
