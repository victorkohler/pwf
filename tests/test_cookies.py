# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 18/12/2016
@version: 0.1

Tests covering the core functionality of cookies and functionality
from pwf/cookies.py

"""

import pytest
from datetime import timedelta, datetime
from time import gmtime
from collections import Counter

from pwf.cookies import create_cookie, format_date

class TestCookieCreation(object):
    def setup_method(self, test_method):

        self.key, self.value, self.path = 'test-cookie', '12345', '/'
        self.domain, self.secure, self.httponly = None, True, False
        self.expires = datetime(2016, 12, 21, 22, 56, 01)
        self.max_age = timedelta(days=2)
        self.expected_args = [
                'Expires=Wed, 21-Dec-2016 22:56:01 GMT',
                'test-cookie=12345',
                'Max-Age=172800',
                'Path=/',
                'Secure']

    def test_create_cookie(self):
        cookie = create_cookie(self.key, self.value, self.path, self.expires,
                self.max_age, self.domain, self.secure, self.httponly)

        self.assert_cookie_args(cookie, self.expected_args)

    def test_expire_string(self):
        expires_string = '1482357361'
        cookie = create_cookie(self.key, self.value, self.path, expires_string,
                self.max_age, self.domain, self.secure, self.httponly)

        self.expected_args[0] = 'Expires=1482357361'
        self.assert_cookie_args(cookie, self.expected_args)

    def test_cookie_int(self):
        domain_int = 123456
        cookie = create_cookie(self.key, self.value, self.path, self.expires,
                self.max_age, domain_int, self.secure, self.httponly)

        self.expected_args.append('Domain=123456')
        self.assert_cookie_args(cookie, self.expected_args)

    def test_not_secure_cookie(self):
        not_secure = False
        cookie = create_cookie(self.key, self.value, self.path, self.expires,
                self.max_age, self.domain, not_secure, self.httponly)

        del self.expected_args[4]
        self.assert_cookie_args(cookie, self.expected_args)

    def assert_cookie_args(self, cookie, expected_args):
        assert isinstance(cookie, dict)
        assert len(cookie) == 1
        cookie_args = cookie['Set-Cookie'].split('; ')
        assert Counter(cookie_args) == Counter(expected_args)




class TestDateFormat(object):

    def test_format_timestamp(self):
        date = datetime.fromtimestamp(1482357361)
        formated = format_date(date)
        assert formated == 'Wed, 21-Dec-2016 22:56:01 GMT'

    def test_format_int(self):
        date = 1482357361
        formated = format_date(date)
        assert formated == 'Wed, 21-Dec-2016 21:56:01 GMT'

    def test_format_datetime(self):
        date = datetime(2016, 12, 21, 21, 56, 01)
        formated = format_date(date)
        assert formated == 'Wed, 21-Dec-2016 21:56:01 GMT'

    def test_format_none(self):
        date = None
        formated = format_date(date)
        assert formated == format_date(gmtime())

    def test_format_string(self):
        date = 'Tomorrow'
        with pytest.raises(AttributeError) as attr_err:
            format_date(date)
        assert attr_err.value.message == "'str' object has no attribute 'tm_wday'"


