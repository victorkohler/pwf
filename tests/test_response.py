# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""
import pytest
import json
from collections import Counter

from pwf.response import Response
from mocks.make_response import make_response


class TestResponseObject(object):

    def setup_method(self, test_method):
        self.response = Response()

    def test_empty_response(self):
        assert isinstance(self.response, Response)
        assert isinstance(self.response.headers, dict)
        assert self.response.code == 200
        assert not self.response.make_response
        assert not self.response.data

    def test_create_with_params(self):
        header = {'X-Custom-Header': 'custom-value'}
        data = 'This is my data'
        response = Response(data=(data, header), code=201)
        assert response.headers == header
        assert response.data == 'This is my data'
        assert response.code == 201

    def test_data_swe(self):
        self.response.data = 'äöå'
        self.response.make_response = make_response
        render_data = self.response.render()
        assert render_data == 'äöå'

    def test_data_json(self):
        data = {'success': True, 'data': 'åäö'}
        self.response.data = json.dumps(data)
        self.response.make_response = make_response
        render_data = self.response.render()
        assert render_data == '{"data": "\u00e5\u00e4\u00f6", "success": true}'

    def test_set_headers(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['X-Custom-Header'] = 'custom-value'
        assert self.response.headers == {
                'Content-Type': 'application/json', 
                'X-Custom-Header': 'custom-value'}

    def test_set_cookie(self):
        self.response.set_cookie('session', 'abc123')
        assert self.response.headers == {'Set-Cookie': 'session=abc123; Path=/'}

    def test_error_render(self):
        self.response.code = 404
        self.response.make_response = make_response
        render_data = self.response.render()
        assert render_data == '404 Not Found'

    def test_render(self):
        self.response.data = 'This is my data'
        self.response.make_response = make_response
        render_data = self.response.render()
        assert render_data == self.response.data

    def test_repr(self):
        assert self.response.__repr__() == \
                ("Response({'headers': {}, 'code': 200, 'data': '',"
                 " 'make_response': None})")
