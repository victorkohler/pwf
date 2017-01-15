# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1
"""


import shutil
import json
from tempfile import TemporaryFile
from io import BytesIO


class FileWrapper(object):
    """Wrapper around a wsgi.input filestream. 
    It adds functionality for retrieving the filename
    and saving the file to disk.
    
    This can also be used to wrap binary data and treat
    it like a file object.
    """

    def __init__(self, file, filename=None, name=None,
                 mimetype=None, headers=None):

        if isinstance(file, str):
            self.file = BytesIO(file)
        else:
            self.file = file

        self.filename = filename
        self.name = name
        self.headers = headers
        self.mimetype = mimetype

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
            shutil.copyfileobj(self.file, dest, self.buffer_size)
        finally:
            dest.close()

    def seek(self, pos):
        """Seek the file to the specified position (pos)"""
        self.file.seek(pos)

    def read(self, length=-1):
        """Read the file to the specified length or EOF"""
        return self.file.read(length)
        
    def close(self):
        """Close the file. If you try to access the FileWrapper
        object after it's been closed it will raise an ValueError.
        """
        try:
            self.file.close()
        except Exception:
            pass

    def readline(self):
        return self.file.readline()


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

