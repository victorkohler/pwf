# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""

#import Cookie
from collections import namedtuple

def create_cookie(key, value='', path='/', expires=None, max_age=None,
            domain=None, secure=False, httponly=False):
    """Generates a WSGI compatible cookie dictionary. Key and value are 
    requred and we then loop through the additional ones to check what
    to add and how.
    """

    Attribute = namedtuple('Attribute', ['name', 'value', 'str_value'])

    attributes = (Attribute('Domain', domain, True),
                  Attribute('Expires', expires, False,),
                  Attribute('Max-Age', max_age, False),
                  Attribute('Secure', secure, None),
                  Attribute('HttpOnly', httponly, None),
                  Attribute('Path', path, False))
       
    buf = [key + '=' + value]
    for a in attributes:
        
        # If a.str_value is None but there is a value set we only add the
        # name to the cookie (Example: Secure rather than Secure=True)
        if a.str_value is None:
            if a.value:
                buf.append(a.name)
            continue

        if a.value is None:
            continue
        
        if not isinstance(a.value, (bytes, bytearray)):
            a.value = bytes(a.value)

        attribute_string = '{}={}'.format(a.name, a.value)
        buf.append(bytes(attribute_string))
    
    cookie_string = '; '.join(buf)
    cookieheader = {'Set-Cookie': cookie_string}

    #cookie = Cookie.SimpleCookie()
    #cookie[key] = value
    #cookieheader = {'Set-Cookie': cookie[key].OutputString()}
    return cookieheader


