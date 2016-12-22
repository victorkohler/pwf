
import pytest
import json
from collections import Counter

from pwf.helpers import json_response


class TestHelperFunctions(object):

    def setup_method(self, test_method):
        self.headers = {'Content-Type': 'text/html', 'Access-Control-Max-Age': 1728000}

    def test_json_response(self):
        data = {'success': True, 'data': 'This is some response data'} 
        json_data = json_response(data, self.headers)
        assert isinstance(json_data, tuple)
        return_data, return_headers = json_data

        assert return_data == '{"data": "This is some response data", "success": true}'
        assert return_headers['content-type'] == 'application/json'
        assert return_headers['Access-Control-Max-Age'] == '1728000'


    def test_json_no_headers(self):
        data = {'success': True, 'data': 'This is some response data'} 
        json_data = json_response(data)
        return_data, return_headers = json_data

        assert return_headers == {'content-type': 'application/json'}
        assert return_data == '{"data": "This is some response data", "success": true}'



