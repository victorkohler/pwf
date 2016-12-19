# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1
"""

import httplib
import helpers

class Response(object):
    """ Response object is responsible for iterating the make_response and
    returning the view data

    :params code, the status code
    :params data, the raw data rendered from the view
    """

    def __init__(self, make_response=None, code=200, data=''):
        """The Response object can be instantiated in one of two ways.
        Either it gets created manually in the view function by the user
        to add custom headers, cookies or response codes.

        Or it gets created automatically once the view function returns
        some data.

        To create the response object from the view and set a custom
        header:

            resp = app.make_response(data)
            resp['x-custom-header'] = 'my-cookie'

        For the view data we're currently supporting either a tuple with
        both the returned data and a dictionary of headers OR just the 
        returned data.

        Support for view defined status codes might come later.
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

    def set_cookie(self, key, value, path=None, expiration=None):
        """Creates a cookie tuple and adds it to the headers.
        This function is ment to be used in the view function like so:
        
            resp = make_response(data)
            resp.set_cookie('key', 'value')
        """

        cookie = helpers.create_cookie(key, value, path, expiration)
        self.headers.update(cookie)

    def render(self):
        """Renders the final response back to the server with status code,
        headers and data. Transform headers and codes into WSGI compatible
        format.
        
        If status code is 5xx or 4xx no view data is returned
        """

        # If the content type is not specified, we set
        # it to text/html as the default
        if 'content-type' not in map(lambda x:x.lower(), self.headers):
            self.headers['Content-Type'] = 'text/html'

        # Set headers as list of tuples
        self.headers = [(k, v) for k, v in self.headers.items()]

        # httplib.responses maps the HTTP 1.1 status codes to W3C names.
        # Output example: '200 OK' or '404 Not Found'
        # TODO: Handle unspupported status code
        resp_code = '{} {}'.format(self.code, httplib.responses[self.code])

        if str(self.code)[0] in ['4', '5']:
            self.make_response(resp_code, self.headers)
            return resp_code.encode('utf-8')

        try:
            data = bytes(self.data)
        except Exception:
            data = str(self.data).encode('utf-8')
        
        self.make_response(resp_code, self.headers)
        return data

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__dict__)

