# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1

This module implements a series of utilities not used directly
but PWF but that can come in handy in the view function.
"""

import json

def json_response(data, headers=None):
    """Generates a valid JSON response
    along with the correct content-type header.

    @param data: A dict that will be converted to JSON.
    @param headers: A dict of additional reponse headers.

    Note: If the header param already contains a content-type
    it will be removed and replaced by the 'application/json' header.
    """
    if isinstance(headers, dict):
        content_types = [key for key in headers.keys() if key.lower() == 'content-type']
        for key in content_types:
            headers.pop(key)
    else:
        headers = {}

    # Turn header values into strings
    for header, value in headers.iteritems():
        if not isinstance(value, str):
            headers[header] = bytes(value)


    headers['content-type'] = 'application/json'
    return json.dumps(data), headers

