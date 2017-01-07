# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 07/01/2017
@version: 0.1
"""

import pytest
from pwf.stack import _app_stack


def test_appstack_push():
    item = dict
    _app_stack.push(item)
    assert _app_stack.top == dict

def test_appstack_pop():
    item = int
    _app_stack.push(item)
    popped = _app_stack.pop()
    assert popped == int

def test_appstack_top():
    item = list
    _app_stack.push(item)
    state = _app_stack.items
    top = _app_stack.top
    assert top == list
    assert _app_stack.items == state

def test_appstack_empty():
    _app_stack.push(str)
    assert not _app_stack.is_empty
    _app_stack.reset()
    assert _app_stack.is_empty

def test_appstack_top_fail():
    _app_stack.reset()
    top = _app_stack.top
    assert not top







