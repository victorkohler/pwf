# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""

import json
import Cookie

def json_response(data, headers=None):
    """Function that generates a valid JSON response
    along with the correct content-type header.

    @param data: A dict that will be converted to JSON.
    @param headers: A dict of additional reponse headers.

    Note: If the header param contains a content type it will
    be removed and replaced by the 'application/json' header.
    """

    if isinstance(headers, dict):
        content_types = [key for key in headers.keys() if key.lower() == 'content-type']
        for key in content_types:
            headers.pop(key)
    else:
        headers = {}

    headers['content-type'] = 'application/json'
    return json.dumps(data), headers

def create_cookie(key, value, path=None, expires=None):
    """Generates a WSGI compatible cookie dictionary"""

    cookie = Cookie.SimpleCookie()
    cookie[key] = value
    
    if path:
        cookie[key]['path'] = path
    
    if expires:
        cookie[key]['expires'] = expires

    cookieheader = {'Set-Cookie': cookie[key].OutputString()}
    return cookieheader


