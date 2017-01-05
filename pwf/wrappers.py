# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1
"""


import shutil
import json
from tempfile import TemporaryFile
from StringIO import StringIO


class FileWrapper(object):
    """Wrapper around a wsgi.input filestream. 
    It adds functionality for retrieving the filename
    and saving the file to disk.
    
    This can also be used to wrap binary data and treat
    it like a file object.
    """

    def __init__(self, filestream, filename=None, name=None,
                 content_type=None, headers=None):

        if isinstance(filestream, str):
            self.filestream = StringIO(filestream)
        else:
            self.filestream = filestream

        self.filename = filename
        self.name = name
        self.headers = headers

        if content_type is not None:
            self.content_type = content_type

        self.buffer_size = 16384

    def save(self, dest):
        """Copies the content of the filestream into a file
        in the specified destination. We copy the file
        over in chunks equal to the buffer_size.

        After the file is saved the filewrapper buffer

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

    def seek(self, pos):
        """Seek the file to the specified position (pos)"""
        self.filestream.seek(pos)

    def read(self, length=-1):
        """Read the file to the specified length or EOF"""
        return self.filestream.read(length)
        
    def close(self):
        """Close the file. If you try to access the FileWrapper
        object after it's been closed it will raise an ValueError.
        """
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

