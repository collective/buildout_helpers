# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import requests_mock
from buildout_helpers.testing import BaseTestCase
from buildout_helpers.freeze import freeze
from io import open

import os.path


class TestFreezer(BaseTestCase):

    def test_freezer(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''\
[buildout]
extends= http://example.com/buildout.cfg
''')
        expected1 = '''\
[buildout]
extends= external_buildouts/example.com_buildout.cfg
'''
        expected2 = '''\
# File managed by freeze command from buildout_helpers
# Changes will be overwritten
# ETAG: XXX
# ORIGIN: http://example.com/buildout.cfg
[buildout]'''
        with requests_mock.mock() as m:
            m.get('http://example.com/buildout.cfg', text='''[buildout]''',
                  headers={'Etag': 'XXX'})
            freeze(cfg)

        abs_dir, _ = os.path.split(cfg)
        location = os.path.join(abs_dir,
                                'external_buildouts/example.com_buildout.cfg')
        new_file_contents = open(location, 'r').read()
        old_file_contents = open(cfg, 'r').read()
        self.assertEqual(old_file_contents, expected1)
        self.assertEqual(new_file_contents, expected2)

    def test_freezer_nested(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''\
[buildout]
extends= http://example.com/buildout.cfg
''')
        expected1 = '''\
[buildout]
extends= external_buildouts/example.com_buildout.cfg
'''
        expected2 = '''\
# File managed by freeze command from buildout_helpers
# Changes will be overwritten
# ETAG: None
# ORIGIN: http://example.com/buildout.cfg
[buildout]
extends= external_buildouts/example.com_buildout2.cfg
'''
        with requests_mock.mock() as m:
            m.get('http://example.com/buildout.cfg', text='''[buildout]
extends= http://example.com/buildout2.cfg
''')
            m.get('http://example.com/buildout2.cfg', text='''[buildout]''')
            freeze(cfg)

        abs_dir, _ = os.path.split(cfg)
        new_file_contents = open(os.path.join(abs_dir,
                                              'external_buildouts',
                                              'example.com_buildout.cfg'),
                                 'r').read()
        old_file_contents = open(cfg, 'r').read()
        self.assertEqual(old_file_contents, expected1)
        self.assertEqual(new_file_contents, expected2)

    def test_freezer_caching(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''\
[buildout]
extends= http://example.com/buildout.cfg
''')
        with requests_mock.mock() as m:
            m.get('http://example.com/buildout.cfg', text='''[buildout]''',
                  headers={'Etag': 'XXX'})
            freeze(cfg)
            freeze(cfg)
            last_call = m.request_history[-2]
            self.assertEqual('XXX',
                             last_call._request.headers['If-None-Match'])
