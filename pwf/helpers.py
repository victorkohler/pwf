# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1

Features implemented here are series of utilities not used by
PWF directly but that might come in handy. They are not related
to the PWF core or specific to WSGI.
"""

import json
import time
from functools import wraps


def render_json(data, headers=None):
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


def timed(f):
    """A simple decorator that calculates the amount of time
    a view function takes to execute (in milliseconds). The
    result is printed to sys.stdout.
    """
    @wraps(f)
    def wrapper(*args, **kwds):
        start = time.time()
        result = f(*args, **kwds)
        elapsed = float((time.time() - start) * 1000)
        print '{0} took {1:.2f} ms to finish'.format(f.__name__, elapsed)
        return result
    return wrapper


