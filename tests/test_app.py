# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""

import pytest
import json

from pwf.app import Pwf
from pwf.request import Request
from pwf.response import Response
from mocks.environ import CreateEnviron
from mocks.make_response import make_response


class TestPwfApp(object):
    def setup_method(self, test_method):
        self.app = Pwf()
        self.environ = CreateEnviron()

    def test_basic_routing(self):
        
        @self.app.route('/')
        def view_func(r):
            pass

        @self.app.route('/get')
        def view_func(r):
            pass

        for route_pattern, methods, view_function in self.app.routes:
            assert route_pattern.pattern in ['^/$', '^/get$']
            assert set(methods).issubset(set(['GET', 'POST', 'PUT', 'OPTIONS']))
            assert callable(view_function)

    def test_view(self):

        @self.app.route('/')
        def view_func(r):
            return r

        assert view_func('Hello') == 'Hello'

    def test_call_app(self):

        @self.app.route('/get')
        def view_func(r):
            assert isinstance(r, Request)
            assert r.method == 'GET'
            assert r.headers['REQUEST_METHOD'] == 'GET'

        render_data = self.__fake_request('/get')
        assert render_data == 'None'

    def test_no_path_match(self):

        @self.app.route('/')
        def view_func(r):
            assert r.code == '404'

        render_data = self.__fake_request('/my-page')
        assert render_data == '404 Not Found'

    def test_unsupported_method(self):

        @self.app.route('/post', methods=['POST'])
        def view_func(r):
            assert r.code == '405'

        render_data = self.__fake_request('/post')
        assert render_data == '405 Method Not Allowed'

    def test_response_return(self):

        @self.app.route('/')
        def view_func(r):
            response = Response(data='Hello')
            return response

        render_data = self.__fake_request('/')
        assert render_data == 'Hello'

    def test_make_response(self):
        data = 'Hello World'
        resp = self.app.make_response(data)
        assert isinstance(resp, Response)
        assert resp.data == 'Hello World'
        assert not resp.make_response

    def test_string_return(self):

        @self.app.route('/get')
        def view_func(r):
            return 'Hello World'

        render_data = self.__fake_request('/get')
        assert render_data == 'Hello World'

    def test_json_return(self):

        @self.app.route('/json')
        def view_func(r):
            return json.dumps({'success': True})

        render_data = self.__fake_request('/json')
        assert render_data == '{"success": true}'

    def test_repr(self):
        assert self.app.__repr__() == 'Pwf()'

    def test_config(self):
        self.app.config.update(dict(DEBUG=True))
        assert self.app.config['DEBUG']
        
    def test_config_from_json(self):
        self.app.config.from_json_file('/var/www/pwf/tests/config.json')
        assert self.app.config['DEBUG']

    def __fake_request(self, path):
        self.environ.path_info = path
        render = self.app(self.environ, make_response)
        return render



