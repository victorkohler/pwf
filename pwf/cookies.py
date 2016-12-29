# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""

from time import gmtime
from collections import namedtuple
from datetime import datetime, timedelta

def create_cookie(key, value='', path='/', expires=None, max_age=None,
            domain=None, secure=False, httponly=False):
    """Generates a WSGI compatible cookie dictionary. Key and value are 
    requred and we then loop through the additional ones to check what
    to add and how.
    """
    if isinstance(max_age, timedelta):
        max_age = (max_age.days * 60 * 60 * 24) + max_age.seconds
  
    if expires and not isinstance(expires, str):
        expires = format_date(expires)

    attributes = (('Domain', domain, True),
                  ('Expires', expires, False,),
                  ('Max-Age', max_age, False),
                  ('Secure', secure, None),
                  ('HttpOnly', httponly, None),
                  ('Path', path, False))
       
    buf = [key + '=' + value]
    for name, value, use_value in attributes:
        
        # If use_value is None but value is set we only add the
        # name to the cookie (Example: Secure rather than Secure=True)
        if use_value is None:
            if value:
                buf.append(name)
            continue # pragma: no cover

        if value is None:
            continue
        
        if not isinstance(value, (bytes, bytearray)):
            value = bytes(value)

        attribute_string = '{}={}'.format(name, value)
        buf.append(bytes(attribute_string))
    
    cookie_string = '; '.join(buf)
    cookieheader = {'Set-Cookie': cookie_string}

    return cookieheader



def format_date(date):
    """Format to Wed, 21-Dec-2016 21:28:34 GMT.
    Accepts int, float or datetime object.
    """
    if date is None:
        date = gmtime()
    elif isinstance(date, datetime):
        date = date.utctimetuple()
    elif isinstance(date, (int, float)):
        date = gmtime(date)

    return '%s, %02d%s%s%s%s %02d:%02d:%02d GMT' % (
        ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')[date.tm_wday],
        date.tm_mday, '-',
        ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
        'Oct', 'Nov', 'Dec')[date.tm_mon - 1],
        '-', str(date.tm_year), date.tm_hour, date.tm_min, date.tm_sec
        )




