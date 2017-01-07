# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1

Defines custom exceptions used by Pwf or that can be used
in the view fucntion.
"""


class HTTPException(Exception):

    code = None
    description = None

    def __init__(self, code=None, description=None):
        Exception.__init__(self)

    @property
    def respcode(self):
        return self.code


class NotFound(HTTPException):
    code = 404
    description = ''


class MethodNotAllowed(HTTPException):
    code = 405
    description = ''


class InternalError(HTTPException):
    code = 500
    description = ''


class RequestEntityTooLarge(HTTPException):
    code = 413
    description = ''

