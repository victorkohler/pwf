# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1
"""

import cgi
import urlparse
import Cookie
from wrappers import FileWrapper

class Request(object):
    """Create a Request object populated with the contents of
    the WSGI environ dictionary.

    This object gets passed to the user defined view function
    to be consumed. 
    """

    def __init__(self, environ):
        """Set object variables that will be accessible
        in the view function.
        """
        self.files = {}
        self.environ = environ
        self.headers = self.__parse_headers(environ)
        self.query = self.__parse_query(environ)
        self.data = self.__parse_data(environ)
        self.method = self.__parse_method(environ)
        self.cookies = self.__parse_cookies(environ)


    def __parse_cookies(self, environ):
        """Get cookies from environ and return a dict with 
        keys and values.
        """
        parsed_cookies = {}
        cookies = Cookie.SimpleCookie(environ.get('HTTP_COOKIE', ''))
        for key in cookies:
            parsed_cookies[key] = cookies[key].value

        return parsed_cookies

    def __parse_headers(self, environ):
        """We parse the headers from the WSGI environ and
        return only the wanted ones defined in wanted_headers list
        plus any HTTP headers.
        """
        length = environ.get('CONTENT_LENGTH', 0)
        headers = { 'CONTENT_LENGTH': 0 if not length else int(length) }

        wanted_headers = ['REQUEST_METHOD', 'PATH_INFO', 'REMOTE_ADDR', 
                'REMOTE_HOST', 'CONTENT_TYPE']

        for k, v in environ.items():
            # TODO: Add support for custom headers
            if k in wanted_headers or k.startswith('HTTP'):
                headers[k] = v

        return headers

    def __parse_method(self, environ):
        """Return the current request method as a string.
        For example 'GET' or 'OPTIONS'
        """
        request_method = environ['REQUEST_METHOD']
        return request_method

    def __parse_query(self, environ):
        """Parse a query string into a dictionary."""
        query = urlparse.parse_qs(environ['QUERY_STRING'])

        # Only select the first value for any give query variable.
        # Perhaps support multiple values in the future 
        unique_variables = {k: v[0] for k, v in query.items()}
        return unique_variables

    def __parse_data(self, environ):
        """Parse the request body data based on content type.
        
        If the request is form data we use cgi.FieldStorage to parse it.
        If it's raw data (json, xml, javascript ect) we just read it from
        environ[wsgi.input] and return it as is.
        
        If no data is sent we return an empty dict.
        """
        content_type = environ['CONTENT_TYPE'].lower()

        if 'form' in content_type:
            return self.__parse_form(environ)
        else:
            length = self.headers['CONTENT_LENGTH']
            return environ['wsgi.input'].read(length)

    def __parse_form(self, environ):
        """Parse form data. If a file is included we wrap it using
        the FileWrapper and add it to self.files. If it's regular
        form data we add the key and value to the data dict
        """
        data = {}
        env_data = cgi.FieldStorage(environ['wsgi.input'], environ=environ,
                keep_blank_values=True)

        for k in env_data.list:
            # NOTE: Perhaps add support application/x-www-form-urlencoded
            # in the future.
            if isinstance(k, cgi.MiniFieldStorage):
                return None

            if k.filename:
                filewrapper = FileWrapper(k.file, k.filename, k.name)
                self.files[k.name] = filewrapper
                data[k.name] = k.file
            else:
                data[k.name] = k.value

        return data

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__dict__)

