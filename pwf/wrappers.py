# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1
"""


import shutil


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
        """
        Copies the content of the filestream into a file
        in the specified destination. We copy the file
        over in chunks equal to the buffer_size.

        Args:
            dest (str): The path where we save the file.
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

