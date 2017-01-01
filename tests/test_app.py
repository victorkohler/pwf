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




@pytest.fixture
def app():
    app = Pwf()
    return app


@pytest.fixture
def environ():
    return CreateEnviron()

def test_basic_routing(app, environ):
    @app.route('/')
    def view_func(r):
        pass

    @app.route('/get')
    def view_func(r):
        pass

    for route_pattern, methods, group, view_function in app.routes:
        assert route_pattern.pattern in ['^/$', '^/get$']
        assert set(methods).issubset(set(['GET', 'POST', 'PUT', 'OPTIONS']))
        assert callable(view_function)


def test_view(app, environ):

    @app.route('/')
    def view_func(r):
        return r
    
    assert view_func('Hello') == 'Hello'


def test_call_app(app, environ):

    @app.route('/get')
    def view_func(r):
        assert isinstance(r, Request)
        assert r.method == 'GET'
        assert r.headers['REQUEST_METHOD'] == 'GET'

    render_data = fake_request('/get', app, environ)
    assert render_data == 'None'


def test_no_path_match(app, environ):

    @app.route('/')
    def view_func(r):
        assert r.code == '404'

    render_data = fake_request('/my-page', app, environ)
    assert render_data == '404 Not Found'


def test_unsupported_method(app, environ):

    @app.route('/post', methods=['POST'])
    def view_func(r):
        assert r.code == '405'

    render_data = fake_request('/post', app, environ)
    assert render_data == '405 Method Not Allowed'


def test_response_return(app, environ):

    @app.route('/')
    def view_func(r):
        response = Response(data='Hello')
        return response

    render_data = fake_request('/', app, environ)
    assert render_data == 'Hello'


def test_make_response(app, environ):
    data = 'Hello World'
    resp = app.make_response(data)
    assert isinstance(resp, Response)
    assert resp.data == 'Hello World'
    assert not resp.make_response


def test_string_return(app, environ):

    @app.route('/get')
    def view_func(r):
        return 'Hello World'

    render_data = fake_request('/get', app, environ)
    assert render_data == 'Hello World'


def test_json_return(app, environ):

    @app.route('/json')
    def view_func(r):
        return json.dumps({'success': True})

    render_data = fake_request('/json', app, environ)
    assert render_data == '{"success": true}'


def test_first(app, environ):
    @app.route('/')
    def view_func(r):
        return 'Hello World'

    @app.first()
    def first_func(r):
        return 'FIRST'

    render_data = fake_request('/', app, environ)
    assert render_data == 'FIRST'


def test_first_group(app, environ):
        
    @app.route('/')
    def view_func(r):
        return 'Hello World'

    @app.route('/group', group='one')
    def group_func(r):
        return 'Hello Group'

    @app.first()
    def first_func(r):
        global my_value
        my_value = 'first'
        
    @app.first(group='one')
    def group_one_func(r):
        return 'Group one!'


    render_data_1 = fake_request('/', app, environ)
    render_data_2 = fake_request('/group', app, environ)

    assert render_data_1 == 'Hello World'
    assert render_data_2 == 'Group one!'
    assert my_value == 'first'


def test_last(app, environ):
    @app.route('/')
    def view_func(r):
        return 'Hello world'

    @app.last()
    def last_func(r):
        r.data = 'Hello Last'
        return r

    render_data = fake_request('/', app, environ)
    assert render_data == 'Hello Last'
       

def test_last_group(app, environ):

    @app.route('/')
    def view_func(r):
        return 'Hello World'

    @app.route('/group', group='one')
    def group_func(r):
        return 'Hello Group'

    @app.last()
    def last_func(r):
        global my_value 
        my_value = 'last'

    @app.last(group='one')
    def group_one_func(r):
        r.data = 'Group one!'

    render_data_1 = fake_request('/', app, environ)
    render_data_2 = fake_request('/group', app, environ)

    assert render_data_1 == 'Hello World'
    assert render_data_2 == 'Group one!'
    assert my_value == 'last'


def test_repr(app):
    assert app.__repr__() == 'Pwf()'


def test_config(app):
    app.config.update(dict(DEBUG=True))
    assert app.config['DEBUG']


def test_config_from_json(app):
    app.config.from_json_file('/var/www/pwf/tests/config.json')
    assert app.config['DEBUG']


def fake_request(path, app, environ):
    environ.path_info = path
    render = app(environ, make_response)
    return render

