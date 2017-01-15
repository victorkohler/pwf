# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""


import pytest
import json
import time
from collections import Counter
from mock import Mock
from pwf.helpers import render_json, timed


@pytest.fixture
def headers():
    headers = {'Content-Type': 'text/html', 'Access-Control-Max-Age': 1728000}
    return headers


def test_json_response(headers):
    data = {'success': True, 'data': 'This is some response data'} 
    json_data = render_json(data, headers)
    assert isinstance(json_data, tuple)
    return_data, return_headers = json_data

    assert return_data == '{"data": "This is some response data", "success": true}'
    assert return_headers['content-type'] == 'application/json'
    assert return_headers['Access-Control-Max-Age'] == '1728000'


def test_json_no_headers(headers):
    data = {'success': True, 'data': 'This is some response data'} 
    json_data = render_json(data)
    return_data, return_headers = json_data

    assert return_headers == {'content-type': 'application/json'}
    assert return_data == '{"data": "This is some response data", "success": true}'


def test_timed(monkeypatch):
    mock = Mock(return_value=1483203681.162797)
    monkeypatch.setattr('time.time', mock)

    @timed
    def func():
        return True

    f = func()
    assert f
    assert mock.called



