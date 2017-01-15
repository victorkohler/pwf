# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1
"""

import cgi
import urlparse
import json
import Cookie
from io import BytesIO
from tempfile import TemporaryFile

from wrappers import FileWrapper
from utils import cached_property
from stack import _app_stack
from exceptions import RequestEntityTooLarge


class Request(object):
    """Create a Request object populated with the contents of
    the WSGI environ dictionary.

    This object gets passed to the user defined view function
    to be consumed. 
    """

    def __init__(self, environ):
        """Set object variables that will be accessible
        in the view function.

        self.stream holds the cached wsgi.input as a file-like object.
        """
        self.stream = self.__cache_stream(environ)
        self.environ = environ
        self.headers = self.__parse_headers(environ)
        self.content_length = self.__parse_content_length(environ)
        self.mimetype, self.options = self.__parse_content_type(environ)
        self.method = self.__parse_method(environ)
        self.cookies = self.__parse_cookies(environ)
        self.query = self.__parse_query(environ)
        #self.json = None
        
        # Defines methods used by __parse_data depending on mime-type
        self.parse_methods = {
            'multipart/form-data': self.__parse_form,
            'application/x-www-form-urlencoded': self.__parse_form
            }

    def __parse_cookies(self, environ):
        """Get cookies from environ and return a dict with 
        keys and values.
        """
        parsed_cookies = {}
        cookies = Cookie.SimpleCookie(environ.get('HTTP_COOKIE', ''))
        for key in cookies:
            parsed_cookies[key] = cookies[key].value

        return parsed_cookies

    def __parse_content_type(self, environ):
        """Parses the HTTP Content-Type header into a typle of
        mimetype and a dictionary of any options.
        
        For example the content-type 'multipart/form-data; charset=UTF-8'
        is parsed into ('multipart/form-data', {'charset': 'utf-8'})
        
        The word "Content-Type" is used to refer to the HTTP header
        with both MIME and options, while "mimetype" refers to the
        MIME value only.
        """
        ct_value = environ.get('CONTENT_TYPE', '').lower()
        if not ct_value:
            return '', {}

        mimetype, options = cgi.parse_header(ct_value)
        return mimetype, options
        

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
            if k in wanted_headers or k.startswith('HTTP'):
                headers[k] = v
        
        # TODO: Add support for parsed headers. Parse
        # "HTTP_X_CUSTOM-HEADER" to "X-Custom-Header"

        return headers

    def __parse_content_length(self, environ):
        try:
            cl = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            cl = 0

        return cl
    

    def __parse_method(self, environ):
        """Return the current request method as a string.
        For example 'GET' or 'OPTIONS'
        """
        request_method = environ['REQUEST_METHOD']
        return request_method

    def __parse_query(self, environ):
        """Parse a query string into a dictionary."""
        qs = environ.get('QUERY_STRING', None)
        query = urlparse.parse_qs(qs)

        # Only select the first value for any give query variable.
        # Perhaps support multiple values in the future 
        unique_variables = {k: v[0] for k, v in query.items()}
        return unique_variables
    
    def __parse_data(self, environ, parse_form=False):
        """Parses the data from the WSGI environ object depending on
        the mimetype. If no parse method is defined for a
        particular mimetype we fall back to return the
        data as a string.
        """

        length = self.content_length

        if parse_form is not True:
            return self.get_stream.read(length)

        parse_method = self.parse_methods.get(self.mimetype, None)

        if parse_method is not None:
            data = parse_method(environ)
        else:
            data = self.get_stream.read(length)

        return data


    def __parse_form(self, environ):
        """Parse form data. If a file is included we wrap it using
        the FileWrapper and add it to self.files. If it's regular
        form data we add the key and value to the data dict.
        """
        form = {}
        files = {}
        req_d = self.__dict__
        req_d['form'], req_d['files'] = form, files

        env_data = cgi.FieldStorage(self.get_stream, environ=environ,
                keep_blank_values=True)
        
        if not env_data:
            return form

        for k in env_data.list:
            # NOTE: Perhaps add support application/x-www-form-urlencoded
            # in the future.
            if isinstance(k, cgi.MiniFieldStorage):
                return form

            if k.filename:
                headers = dict(k.headers)
                filewrapper = FileWrapper(k.file, k.filename, 
                        k.name, mimetype=k.type, headers=headers)

                files[k.name] = filewrapper
            else:
                form[k.name] = k.value

        return form

    @cached_property
    def data(self):
        """Returns any request data as a form object or
        string, depending on the mimetype"""
        data = self.__parse_data(self.environ, parse_form=True)
        return data

    @cached_property
    def files(self):
        """Returns any uploaded files. Empty if no files where pared"""
        self.__parse_form(self.environ)
        return self.files

    @cached_property
    def form(self):
        """Returns any form data in the request. Emtpy if no form as parsed"""
        self.__parse_form(self.environ)
        return self.form

    @property
    def get_stream(self):
        """Returns the cached stream as a file-like object"""
        self.stream.seek(0)
        return self.stream

    @cached_property
    def json(self):
        """If the mimetype is application/json, parse self.data and
        return a python dictionary"""

        if not self.data:
            return None
    
        if not 'application/json' in self.mimetype:
            return None
       
        try:
            data = json.loads(self.data)
        except ValueError:
            return None

        return data
    
  
    def __cache_stream(self, environ):
        """Caches the query stream so it can be accessed
        multiple times. If the stream was is cached we read
        envrion['wsgi.input'] and store it.
        
        For large files the stream is stored in a temporary file.
        For smaller files (< 500KB) we store the data in memory as a
        BytesIO object.
        """
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            content_length = 0

        stream = environ['wsgi.input'].read(content_length)
        
        # If the stream is large we use a temporary file. If not we
        # just load it into memory
        if content_length > 1024 * 500:
            _stream_cache = TemporaryFile('wb+')
            _stream_cache.write(stream)
            _stream_cache.seek(0)
        else:
            _stream_cache = BytesIO(stream)

        return _stream_cache


    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.__dict__)
