# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""

import StringIO
from io import BytesIO


class CreateEnviron(object):
    """Creates a fake environ class that can be used for testing."""

    server_protocol = 'HTTP/1.1'
    wsgi_version = (1, 0)

    def __init__(self, path='/', query_string='', method='GET',
                 content_type='text/html', content_length=None,
                 headers=None, data=''):

            self.environ = {
                    'REQUEST_METHOD': method,
                    'PATH_INFO': path,
                    'REQUEST_URI': path,
                    'QUERY_STRING': query_string,
                    'CONTENT_TYPE': content_type,
                    'CONTENT_LENGTH': content_length,
                    'HTTP_CONTENT_TYPE': content_type,
                    'HTTP_CACHE_CONTROL': 'no-cache',
                    }

            wsgi_input_data = self._create_wsgi_input(data)
            self.environ['wsgi.input'], self.environ['CONTENT-LENGTH'] \
                = wsgi_input_data

    def get(self, key, default):
        if key in self.environ:
            return self.environ[key]
        else:
            return default

    def items(self):
        for key, value in self.environ.iteritems():
            yield (key, value)

    def __getitem__(self, item):
        return self.environ[item]

    @property
    def path_info(self):
        return self.environ['PATH_INFO']

    @path_info.setter
    def path_info(self, value):
        self.environ['PATH_INFO'] = value

    def _create_wsgi_input(self, data):
        wsgi = StringIO.StringIO()
        wsgi.write(data)
        wsgi.seek(0)
        return wsgi, len(data)
