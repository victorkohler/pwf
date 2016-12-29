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


def test_parse_query(environ, req):
    environ = {'QUERY_STRING': 'id=foo&name=bar'}
    parsed_data = req._Request__parse_query(environ)
    assert isinstance(parsed_data, dict)
    assert parsed_data['id'] == 'foo'
    assert parsed_data['name'] == 'bar'


def test_parse_method(environ, req):
    environ = {'REQUEST_METHOD': 'OPTIONS'}
    parsed_data = req._Request__parse_method(environ)
    assert parsed_data == 'OPTIONS'


def test_form_data(environ, req):
    data = (b'--foo\r\nContent-Disposition: form-field; name=foo\r\n\r\n'
            b'Hello World\r\n'
            b'--foo\r\nContent-Disposition: form-field; name=bar\r\n\r\n'
            b'baz\r\n--foo--')

    environ = {'REQUEST_METHOD': 'POST',
            'CONTENT_TYPE': 'multipart/form-data; boundary=foo',
            'wsgi.input': BytesIO(data)}

    parsed_data = req._Request__parse_data(environ)
    assert isinstance(parsed_data, dict)
    assert parsed_data['foo'] == 'Hello World'
    assert parsed_data['bar'] == 'baz'


def test_simple_form_data(environ, req):
    data = 'parameter=value&also=another'

    environ = {'REQUEST_METHOD': 'POST',
               'CONTENT_TYPE': 'application/x-www-form-urlencoded',
               'wsgi.input': BytesIO(data)}

    parsed_data = req._Request__parse_data(environ)
    assert not parsed_data


@pytest.fixture
def file_environ():
    data = (b'--foo\r\n'
            b'Content-Disposition: form-data; name="foo"; \
                    filename="foo.txt"\r\n'
            b'X-Custom-Header: blah\r\n'
            b'Content-Type: text/plain; charset=utf-8\r\n\r\n'
            b'file contents, just the contents\r\n'
            b'--foo--')

    file_environ = {'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': 'multipart/form-data; boundary=foo',
                    'wsgi.input': BytesIO(data)}

    return file_environ


def test_form_file(environ, req, file_environ):
    parsed_data = req._Request__parse_data(file_environ)
    assert parsed_data['foo'].read() == 'file contents, just the contents'
    assert isinstance(req.files['foo'], FileWrapper)
    assert req.files['foo'].filename == 'foo.txt'


def test_save_file(req, monkeypatch, file_environ):
    mock_copy = Mock(return_value=True)
    mock_open = Mock(return_value=MockOpen())
    monkeypatch.setattr('shutil.copyfileobj', mock_copy)
    monkeypatch.setattr('__builtin__.open', mock_open)

    parsed_data = req._Request__parse_data(file_environ)
    req.files['foo'].save('asd')
    assert mock_copy.called
    assert mock_open.called


def test_close_filewrapper(req, monkeypatch):
    filewrapper = FileWrapper('String')
    filewrapper.close()


def test_json_parser(req):
    req.data = '{"title": "Example", "data": {"first": "second"}}'
    data = req.json_data
    assert data is None

    req.environ['CONTENT_TYPE'] = 'application/json'
    assert not req.json
    data = req.json_data
    assert isinstance(data, dict)
    assert data['title'] == 'Example'
    assert data['data']['first'] == 'second'

    data = req.json_data
    assert isinstance(data, dict)
    assert req.json


def test_json_parser_fail(req):
    req.data = 'Just a string'
    req.environ['CONTENT_TYPE'] = 'application/json'
    data = req.json_data
    assert data is None


def test_repr(req):
    req.__repr__()
