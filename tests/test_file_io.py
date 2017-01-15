# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1
"""


import pytest
from mock import Mock
import shutil
from io import BytesIO
from StringIO import StringIO
import tempfile

from pwf.request import Request
from pwf.wrappers import FileWrapper
from mocks.environ import CreateEnviron
from mocks.builtin import MockOpen


@pytest.fixture
def environ():
      return CreateEnviron(path='/get')


@pytest.fixture
def req(environ):
    req = Request(environ.environ)
    return req


@pytest.fixture
def file_environ():
    data = (b'--foo\r\n'
            b'Content-Disposition: form-data; name="foo"; \
                    filename="foo.txt"\r\n'
            b'X-Custom-Header: blah\r\n'
            b'Content-Type: text/plain; charset=utf-8\r\n\r\n'
            b'file contents, just the contents\r\n'
            b'--foo--')

    file_environ = {'REQUEST_METHOD': 'POST', 'QUERY_STRING': '', 
                    'CONTENT_TYPE': 'multipart/form-data; boundary=foo',
                    'CONTENT_LENGTH': len(data),
                    'wsgi.input': BytesIO(data)}

    return file_environ


def test_cache_stream(environ, req, file_environ):
    data = 'my data'
    f = StringIO(data)
    environ = {'wsgi.input': f, 'CONTENT_LENGTH': len(data)}
    cached_stream = req._Request__cache_stream(environ)
    assert isinstance(cached_stream, BytesIO)
    assert cached_stream.read() == data


def test_large_stream(environ, req):
    data = 'x' * 1024 * 1024    
    f = StringIO(data)
    environ = {'wsgi.input': f, 'CONTENT_LENGTH': len(data)}
    cached_stream = req._Request__cache_stream(environ)
    assert isinstance(cached_stream, file)


def test_form_file(environ, req, file_environ):
    file_req = Request(file_environ)
    parsed_data = file_req._Request__parse_data(file_environ)
    assert file_req.files['foo'].read() == 'file contents, just the contents'
    assert isinstance(file_req.files['foo'], FileWrapper)
    assert file_req.files['foo'].filename == 'foo.txt'


def test_binary_file(req, file_environ):
    data = BytesIO(b'Demogorgon')
    cl = len(b'Demogorgon')

    file_environ['wsgi.input'] = data
    file_environ['CONTENT_TYPE'] = 'application/octet-stream'
    file_environ['CONTENT_LENGTH'] = cl
   
    file_req = Request(file_environ)
    my_file = FileWrapper(file_req.data)
    assert file_req.data == 'Demogorgon'
    assert file_req.get_stream.read() == 'Demogorgon'
    assert my_file.read() == 'Demogorgon'


def test_save_file(req, monkeypatch, file_environ):
    mock_copy = Mock(return_value=True)
    mock_open = Mock(return_value=MockOpen())
    monkeypatch.setattr('shutil.copyfileobj', mock_copy)
    monkeypatch.setattr('__builtin__.open', mock_open)

    file_req = Request(file_environ)
    parsed_data = req._Request__parse_data(file_environ)
    file_req.files['foo'].save('asd')
    assert mock_copy.called
    assert mock_open.called


def test_file_readline():
    stream = 'This is one line\nThis is anoter\nAnd a third'
    f = FileWrapper(stream)
    assert f.readline() == 'This is one line\n'
    f.close()


def test_seek_file():
    stream = 'This is a binary string'
    f = FileWrapper(stream)
    f.seek(10)
    assert f.read() == 'binary string'
    f.seek(0)
    assert f.read() == stream
    f.close()


def test_close_filewrapper(req, monkeypatch):
    filewrapper = FileWrapper('String')
    filewrapper.close()


def test_close_fail(req, monkeypatch):
    filewrapper = FileWrapper(123)
    filewrapper.close()
