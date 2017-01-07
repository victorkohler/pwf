# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1
"""

import httplib
import helpers
import cookies

class Response(object):
    """Used to set and return data back to the server. The Response object
    can be instantiated in one of two ways:

    1. It is created manually in the view function to add custom headers, 
    cookies or response codes.
    
    2. It gets created automatically once the view function returns
    some data.

    Create the response object from the view using app.make_response(data)
    """

    def __init__(self, make_response=None, code=200, data=''):
        """For the view data we're currently supporting either a tuple with
        both the returned data and a dictionary of headers or just the 
        returned data.
        """
        if isinstance(data, tuple):
            self.data = data[0]
            headers = data[1]
        else:
            self.data = data
            headers = {}

        self.headers = headers
        self.code = code
        self.make_response = make_response

    def set_cookie(self, key, value='', path='/', expires=None, max_age=None,
                domain=None, secure=False, httponly=False):
        """Creates a cookie dictionary and adds it to the headers.
        This function is ment to be used in the view function:
        
            resp = make_response(data)
            resp.set_cookie('key', 'value')
        """
        cookie = cookies.create_cookie(key, value, path, expires, max_age,
                domain, secure, httponly)

        #TODO: Handle multiple cookies
        self.headers.update(cookie)

    def render(self):
        """Renders the final response back to the server with status code,
        headers and data. It aslo transform headers and codes into
        a WSGI compatible format.
        
        If status code is 5xx or 4xx no view data is returned.
        """

        # If the content type is not specified, we set
        # it to text/html as the default
        if 'content-type' not in map(lambda x:x.lower(), self.headers):
            self.headers['Content-Type'] = 'text/html'

        # Set headers as list of tuples
        self.headers = [(k, v) for k, v in self.headers.items()]

        # httplib.responses maps the HTTP 1.1 status codes to W3C names.
        # Output example: '200 OK' or '404 Not Found'
        resp_code = '{} {}'.format(self.code, httplib.responses[self.code])

        if str(self.code)[0] in ['4', '5'] and not self.data:
            self.make_response(resp_code, self.headers)
            return resp_code.encode('utf-8')

        try:
            data = bytes(self.data).encode('utf-8')
        except UnicodeDecodeError:
            data = bytes(self.data)
        
        self.make_response(resp_code, self.headers)
        return data

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__dict__)
