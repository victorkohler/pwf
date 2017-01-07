# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 07/01/2017
@version: 0.1
"""


class AppStack(object):
    
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    @property 
    def top(self):
        try:
            return self.items[-1]
        except (AttributeError, IndexError):
            return None

    @property    
    def is_empty(self):
        return (self.items == [])

    def reset(self):
        self.items = []
    

_app_stack = AppStack()
