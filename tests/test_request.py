# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""

import pytest
from collections import Counter
from io import BytesIO

from pwf.request import Request
from mocks.environ import CreateEnviron


class TestRequestObject(object):
    def setup_method(self, test_method):
        self.environ = CreateEnviron(path='/get')
        self.request = Request(self.environ.environ)

    def test_create_request(self):
        assert self.request.environ == self.environ.environ

    def test_parse_headers(self):
        environ = {'CONTENT_LENGTH': 0, 'REQUEST_METHOD': 'GET',
                   'PATH_INFO': '/get',
                   'CONTENT_TYPE': 'application/json',
                   'X_CUSTOM_HEADER': 'custom-header'}

        parsed_data = self.request._Request__parse_headers(environ)
        del environ['X_CUSTOM_HEADER']
        assert isinstance(parsed_data, dict)
        assert Counter(parsed_data) == Counter(environ)

    def test_parse_cookies(self):
        data = {'HTTP_COOKIE': 'session=abcd1234'}
        cookies = self.request._Request__parse_cookies(data)
        assert isinstance(cookies, dict)
        assert cookies == {'session': 'abcd1234'}

    def test_parse_query(self):
        environ = {'QUERY_STRING': 'id=foo&name=bar'}
        parsed_data = self.request._Request__parse_query(environ)
        assert isinstance(parsed_data, dict)
        assert parsed_data['id'] == 'foo'
        assert parsed_data['name'] == 'bar'

    def test_parse_method(self):
        environ = {'REQUEST_METHOD': 'OPTIONS'}
        parsed_data = self.request._Request__parse_method(environ)
        assert parsed_data == 'OPTIONS'

    def test_form_data(self):
        data = (b'--foo\r\nContent-Disposition: form-field; name=foo\r\n\r\n'
                b'Hello World\r\n'
                b'--foo\r\nContent-Disposition: form-field; name=bar\r\n\r\n'
                b'baz\r\n--foo--')

        environ = {'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': 'multipart/form-data; boundary=foo',
                'wsgi.input': BytesIO(data)}

        parsed_data = self.request._Request__parse_data(environ)
        assert isinstance(parsed_data, dict)
        assert parsed_data['foo'] == 'Hello World'
        assert parsed_data['bar'] == 'baz'

    def test_form_file(self):
        data = (b'--foo\r\n'
                b'Content-Disposition: form-data; name="foo"; filename="foo.txt"\r\n'
                b'X-Custom-Header: blah\r\n'
                b'Content-Type: text/plain; charset=utf-8\r\n\r\n'
                b'file contents, just the contents\r\n'
                b'--foo--')

        environ = {'REQUEST_METHOD': 'POST',
                   'CONTENT_TYPE': 'multipart/form-data; boundary=foo',
                   'wsgi.input': BytesIO(data)}

        parsed_data = self.request._Request__parse_data(environ)
        assert parsed_data['foo'].read() == 'file contents, just the contents'

    def test_repr(self):
        self.request.__repr__()
        

