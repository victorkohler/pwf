# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""
import sys
sys.path.append('/var/www/pwf')

from pwf.request import Request
import StringIO
from io import BytesIO

class CreateEnviron(object):
    server_protocol = 'HTTP/1.1'
    wsgi_version = (1, 0)
    request_class = Request

    def __init__(self, path='/', query_string='', method='GET',
            content_type='text/html', content_length=None, headers=None, data=''):

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


            self._create_wsgi_input(data)

    def _create_wsgi_input(self, data):
        wsgi = StringIO.StringIO()
        wsgi.write(data)
        wsgi.seek(0)
        self.environ['wsgi.input'] = wsgi
        self.environ['CONTENT_LENGTH'] = len(data)

   


