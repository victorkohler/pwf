# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1
"""


import shutil
import json


class FileWrapper(object):
    """Wrapper around a wsgi.input filestream. 
    It adds functionality for retrieving the filename
    and saving the file to disk.
    """

    def __init__(self, filestream, filename=None, name=None):
        print type(filestream)
        self.name = name
        self.filestream = filestream
        self.filename = filename
        self.buffer_size = 16384

    def save(self, dest):
        """Copies the content of the filestream into a file
        in the specified destination. We copy the file
        over in chunks equal to the buffer_size.

        Args:
            dest (str): The path where we save the file.

        Example usage:
            my_file = request.files['deathstarplans']
            my_file.save('/path/to/save/secret-plans.jpg')

        """
        if isinstance(dest, (str, unicode)):
            dest = open(dest, 'wb')
        try:
            shutil.copyfileobj(self.filestream, dest, self.buffer_size)
        finally:
            dest.close()
        
    def close(self):
        try:
            self.filestream.close()
        except Exception:
            pass

class Config(dict):
    """Subclass of dictionary adding the capability of loading
    the configuration from a json file. The config objects
    can be accessed through "app.config".

    Example:

        app.config['DB_USERNAME'] = 'mos_eisley'
        app.config['DB_PASSWORD'] = 'wretchedhiveofscumandvillany'

    """

    def __init__(self):
        dict.__init__(self or {})

    def from_json_file(self, path):
        with open(path) as json_file:
            data = json.loads(json_file.read())
       
        for k, v in data.iteritems():
            self[k] = v
