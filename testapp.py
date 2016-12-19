# -*- coding: utf-8 -*-
#! /usr/bin/env python
"""
Small example application using the PWF api to
communicate with WSGI
"""

from pwf.app import Pwf
from pwf.helpers import json_response
import json

app = Pwf()

@app.route('/', methods=['GET', 'POST'])
def index(request):
    """Handle both GET and POST request methods.
    GET method returns any query string back as JSON.
    POST method returns posted data back as JSON.
    """

    if request.method == 'GET':
        query = request.query
        return_data = {'method': 'GET', 'query': query}
        return json_response(return_data)
    elif request.method == 'POST':
        data = request.data
        return_data = {'method': 'POST', 'posted_data': data}
        return json_response(return_data)

@app.route('/get', methods=['GET'])
def get(request):
    """Exmaple of creating a response object (resp) in the
    view and adding custom cookie and headers
    """

    data = {'success': True}
    resp = app.make_response(json.dumps(data))
    resp.set_cookie('session', 'abcd1234')
    resp.headers['content-type'] = 'application/json'
    resp.headers['X-Custom-Header'] = 'pwf'
    return resp

@app.route('/post', methods=['POST'])
def post(request):
    data = request.data
    return data

@app.route('/user/<username>', methods=['GET'])
def variable(request, username):
    """Example of using variables in URL and passing
    it into the view function. Returning json with custom
    headers.
    """

    data = {'name': username}
    headers = {'X-Custom-header': 'Pwf'}
    response = json_response(data, headers)
    return response

