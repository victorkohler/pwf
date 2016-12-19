# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""

import json

def json_response(data, headers):
    """Data as dict,
       headers as dict
    """

    if 'content-type' not in map(lambda x:x.lower(), headers):
        headers['content-type'] = 'application/json'

    print 'HERE'
    print headers
    
    #return json.dumps(data), headers



