# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""


import pytest
from mock import Mock
from collections import Counter
import shutil
from io import BytesIO
from StringIO import StringIO
import tempfile

from pwf.request import Request
from pwf.wrappers import FileWrapper
from mocks.environ import CreateEnviron
from mocks.builtin import MockOpen


@pytest.fixture
def environ():
      return CreateEnviron(path='/get')


@pytest.fixture
def req(environ):
    req = Request(environ.environ)
    return req


def test_create_req(environ, req):
    assert req.environ == environ.environ


def test_parse_headers(environ, req):
    environ = {'CONTENT_LENGTH': 0, 'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/get',
               'CONTENT_TYPE': 'application/json',
               'X_CUSTOM_HEADER': 'custom-header'}

    parsed_data = req._Request__parse_headers(environ)
    del environ['X_CUSTOM_HEADER']
    assert isinstance(parsed_data, dict)
    assert Counter(parsed_data) == Counter(environ)


def test_parse_cookies(environ, req):
    data = {'HTTP_COOKIE': 'session=abcd1234'}
    cookies = req._Request__parse_cookies(data)
    assert isinstance(cookies, dict)
    assert cookies == {'session': 'abcd1234'}


def test_parse_content_type(req):
    environ = {'CONTENT_TYPE': 'multipart/form-data; charset=UTF-8'}
    parsed = req._Request__parse_content_type(environ)
    mimetype, options = parsed
    assert isinstance(parsed, tuple)
    assert isinstance(options, dict)
    assert isinstance(mimetype, str)
    assert mimetype == 'multipart/form-data'
    assert options == {'charset': 'utf-8'}


def test_parse_content_type_multi(req):
    environ = {}
    parsed = req._Request__parse_content_type(environ)
    assert isinstance(parsed, tuple)
    assert parsed[0] == ''
    assert parsed[1] == {}


def test_parse_query(environ, req):
    environ = {'QUERY_STRING': 'id=foo&name=bar'}
    parsed_data = req._Request__parse_query(environ)
    assert isinstance(parsed_data, dict)
    assert parsed_data['id'] == 'foo'
    assert parsed_data['name'] == 'bar'


def test_empty_query(req, environ):
    environ.environ['QUERY_STRING'] = ''
    parsed_data = req._Request__parse_query(environ)
    assert isinstance(parsed_data, dict)
    assert len(parsed_data) == 0


def test_parse_method(environ, req):
    environ = {'REQUEST_METHOD': 'OPTIONS'}
    parsed_data = req._Request__parse_method(environ)
    assert parsed_data == 'OPTIONS'


def test_form_data(environ, req):
    data = (b'--foo\r\nContent-Disposition: form-field; name=foo\r\n\r\n'
            b'Hello World\r\n'
            b'--foo\r\nContent-Disposition: form-field; name=bar\r\n\r\n'
            b'baz\r\n--foo--')

    environ = {'REQUEST_METHOD': 'POST', 'QUERY_STRING': '',
            'CONTENT_TYPE': 'multipart/form-data; boundary=foo',
            'wsgi.input': BytesIO(data),
            'CONTENT_LENGTH': len(data)}

    form_req = Request(environ)
    parsed_data = form_req.form
    assert isinstance(parsed_data, dict)
    assert parsed_data['foo'] == 'Hello World'
    assert parsed_data['bar'] == 'baz'


def test_simple_form_data():
    data = 'parameter=value&also=another'

    environ = {'REQUEST_METHOD': 'POST', 'QUERY_STRING': '',
               'CONTENT_TYPE': 'application/x-www-form-urlencoded',
               'wsgi.input': BytesIO(data), 'CONTENT_LENGTH': len(data)}

    form_req = Request(environ)
    parsed_data = form_req._Request__parse_data(environ, parse_form=True)
    assert not parsed_data


def test_form_data_fail(req, environ):
    data = ''
    environ = {'REQUEST_METHOD': 'POST', 'QUERY_STRING': '',
               'CONTENT_TYPE': 'application/octet-stream',
               'wsgi.input': BytesIO(data), 'CONTENT_LENGTH': len(data)}

    form_req = Request(environ)
    parsed_data = form_req._Request__parse_form(environ)
    assert not parsed_data


def test_empty_content_length(environ, req):
    environ.environ['CONTENT_LENGTH'] = ''
    environ.environ['wsgi.input'] = StringIO('')
    data_req = Request(environ)
    parsed_data = data_req._Request__parse_data(environ)
    assert not parsed_data


def test_json_parser(req):
    req.data = '{"title": "Example", "data": {"first": "second"}}'
    data = req.json
    assert data is None

    req.mimetype = 'application/json'
    data = req.json
    assert isinstance(data, dict)
    assert data['title'] == 'Example'
    assert data['data']['first'] == 'second'

    data = req.json
    assert isinstance(data, dict)
    assert req.json


def test_json_parser_fail(req):
    req.data = 'Just a string'
    req.mimetype = 'application/json'
    data = req.json
    assert data is None

    req.data = ''
    req.mimetype = 'application/json'
    data = req.json
    assert data is None


def test_repr(req):
    req.__repr__()
