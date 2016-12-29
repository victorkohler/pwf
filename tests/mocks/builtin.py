# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""


class MockOpen(object):
    """Simulate the builtin open function"""

    def __init__(self):
        pass

    def close(self):
        return True
