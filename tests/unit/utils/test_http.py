# -*- coding: utf-8 -*-
'''
    :codeauthor: Nicole Thomas <nicole@saltstack.com>
'''

# Import Python Libs
from __future__ import absolute_import, unicode_literals, print_function

# Import Salt Testing Libs
from tests.support.unit import TestCase, skipIf
from tests.support.mock import NO_MOCK, NO_MOCK_REASON
from tests.support.helpers import (
    MirrorPostHandler,
    Webserver
)

# Import Salt Libs
import salt.utils.http as http


@skipIf(NO_MOCK, NO_MOCK_REASON)
class HTTPTestCase(TestCase):
    '''
    Unit TestCase for the salt.utils.http module.
    '''
    @classmethod
    def setUpClass(cls):
        cls.post_webserver = Webserver(handler=MirrorPostHandler)
        cls.post_webserver.start()
        cls.post_web_root = cls.post_webserver.web_root

    @classmethod
    def tearDownClass(cls):
        cls.post_webserver.stop()
        del cls.post_webserver

    # sanitize_url tests

    def test_sanitize_url_hide_fields_none(self):
        '''
        Tests sanitizing a url when the hide_fields kwarg is None.
        '''
        mock_url = 'https://api.testing.com/?&foo=bar&test=testing'
        ret = http.sanitize_url(mock_url, hide_fields=None)
        self.assertEqual(ret, mock_url)

    def test_sanitize_url_no_elements(self):
        '''
        Tests sanitizing a url when no elements should be sanitized.
        '''
        mock_url = 'https://api.testing.com/?&foo=bar&test=testing'
        ret = http.sanitize_url(mock_url, [''])
        self.assertEqual(ret, mock_url)

    def test_sanitize_url_single_element(self):
        '''
        Tests sanitizing a url with only a single element to be sanitized.
        '''
        mock_url = 'https://api.testing.com/?&keep_it_secret=abcdefghijklmn' \
                   '&api_action=module.function'
        mock_ret = 'https://api.testing.com/?&keep_it_secret=XXXXXXXXXX&' \
                   'api_action=module.function'
        ret = http.sanitize_url(mock_url, ['keep_it_secret'])
        self.assertEqual(ret, mock_ret)

    def test_sanitize_url_multiple_elements(self):
        '''
        Tests sanitizing a url with multiple elements to be sanitized.
        '''
        mock_url = 'https://api.testing.com/?rootPass=badpassword%21' \
                   '&skipChecks=True&api_key=abcdefghijklmn' \
                   '&NodeID=12345&api_action=module.function'
        mock_ret = 'https://api.testing.com/?rootPass=XXXXXXXXXX' \
                   '&skipChecks=True&api_key=XXXXXXXXXX' \
                   '&NodeID=12345&api_action=module.function'
        ret = http.sanitize_url(mock_url, ['api_key', 'rootPass'])
        self.assertEqual(ret, mock_ret)

    # _sanitize_components tests

    def test_sanitize_components_no_elements(self):
        '''
        Tests when zero elements need to be sanitized.
        '''
        mock_component_list = ['foo=bar', 'bar=baz', 'hello=world']
        mock_ret = 'foo=bar&bar=baz&hello=world&'
        ret = http._sanitize_url_components(mock_component_list, 'api_key')
        self.assertEqual(ret, mock_ret)

    def test_sanitize_components_one_element(self):
        '''
        Tests a single component to be sanitized.
        '''
        mock_component_list = ['foo=bar', 'api_key=abcdefghijklmnop']
        mock_ret = 'foo=bar&api_key=XXXXXXXXXX&'
        ret = http._sanitize_url_components(mock_component_list, 'api_key')
        self.assertEqual(ret, mock_ret)

    def test_sanitize_components_multiple_elements(self):
        '''
        Tests two componenets to be sanitized.
        '''
        mock_component_list = ['foo=bar', 'foo=baz', 'api_key=testing']
        mock_ret = 'foo=XXXXXXXXXX&foo=XXXXXXXXXX&api_key=testing&'
        ret = http._sanitize_url_components(mock_component_list, 'foo')
        self.assertEqual(ret, mock_ret)

    def test_requests_multipart_formdata_post(self):
        '''
        Test handling of a multipart/form-data POST using the requests backend
        '''
        match_this = '{0}\r\nContent-Disposition: form-data; name="fieldname_here"\r\n\r\nmydatahere\r\n{0}--\r\n'
        ret = http.query(
            self.post_web_root,
            method='POST',
            data='mydatahere',
            formdata=True,
            formdata_fieldname='fieldname_here',
            backend='requests'
        )
        body = ret.get('body', '')
        boundary = body[:body.find('\r')]
        self.assertEqual(body, match_this.format(boundary))
