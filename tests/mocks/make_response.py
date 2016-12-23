# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""

import pytest

def make_response(resp_code, headers):
    assert isinstance(resp_code, str)
    assert isinstance(headers, list)
    assert isinstance(headers[0], tuple)
    assert resp_code[0] in ['1','2','3','4','5']


