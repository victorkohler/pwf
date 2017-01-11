# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""

import pytest
from mock import Mock
import shutil
from io import BytesIO
from StringIO import StringIO
import tempfile
import random

from pwf.request import Request
from pwf.wrappers import FileWrapper
from pwf.utils import cached_property
from mocks.environ import CreateEnviron
from mocks.builtin import MockOpen

def test_cached_property():
   
    class Test(object):
        @cached_property
        def rand(self):
            rand = random.random()
            return rand

    test = Test()
    value_one = test.rand
    value_two = test.rand

    assert value_one == value_two

