# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 09/01/2017
@version: 0.1

Implements a set of utilities used throughout Pwf but some
might be useful to use in other circumstances as well.
"""
import logging


class cached_property(property):
    """Extends the built in class property with cache
    functionality. It is used in the same way you would
    the regular property decorator.

    The return value is calculated once and then stored
    in the object. Any subsequent access will return 
    the cached value.

    Example:

    class MyClass(object):
        
        @cached_property
        def method(self):
            return 2

    """

    def __init__(self, func, name=None, doc=None):
        self.__name__ = func.__name__
        #self.__module__ = func.__module__
        #self.__doc__ = func.__doc__
        self.func = func

    def __set__(self, obj, value):
        print obj
        obj.__dict__[self.__name__] = value

    def __get__(self, obj, type=None):
        if obj is None: # pragma: no cover
            return self

        value = obj.__dict__.get(self.__name__, None)
        if value is None:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value



def log(info):
    """TODO: Implement a real loggin solution"""
    print info



