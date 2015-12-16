# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from buildout_helpers.freeze import freeze
from buildout_helpers.testing import BaseTestCase
from io import open

import os.path
import requests_mock


class Config:
    def __init__(self, cfg):
        self.configfile = cfg


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
# ETAG: example
# ORIGIN: http://example.com/buildout.cfg
[buildout]'''
        with requests_mock.mock() as m:
            m.get('http://example.com/buildout.cfg', text='''[buildout]''',
                  headers={'Etag': 'example'})
            freeze(Config(cfg))

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
extends= example.com_buildout2.cfg
'''
        with requests_mock.mock() as m:
            m.get('http://example.com/buildout.cfg', text='''[buildout]
extends= buildout2.cfg
''')
            m.get('http://example.com/buildout2.cfg', text='''[buildout]''')
            freeze(Config(cfg))

        abs_dir, _ = os.path.split(cfg)
        new_file_contents = open(os.path.join(abs_dir,
                                              'external_buildouts',
                                              'example.com_buildout.cfg'),
                                 'r').read()
        old_file_contents = open(cfg, 'r').read()
        self.assertEqual(old_file_contents, expected1)
        self.assertEqual(new_file_contents, expected2)

    def test_relatize_url(self):
        from buildout_helpers.freeze import relativize_url
        a = 'http://www.plone.org/a/b/d'
        b = 'http://www.plone.org/a/b/c'
        self.assertEqual('c', relativize_url(b, a))

    def test_freezer_caching(self):
        expected1 = '''\
# File managed by freeze command from buildout_helpers
# Changes will be overwritten
# ETAG: example
# ORIGIN: http://example.com/buildout.cfg
[buildout]'''
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''\
[buildout]
extends= http://example.com/buildout.cfg
''')
        with requests_mock.mock() as m:
            m.get('http://example.com/buildout.cfg', text='''[buildout]''',
                  headers={'Etag': 'example'})
            freeze(Config(cfg))
            m.get('http://example.com/buildout.cfg', text='''''',
                  status_code=304)
            freeze(Config(cfg))
            last_call = m.request_history[-1]
            self.assertEqual('example',
                             last_call._request.headers['If-None-Match'])
        abs_dir, _ = os.path.split(cfg)
        new_file_contents = open(os.path.join(abs_dir,
                                              'external_buildouts',
                                              'example.com_buildout.cfg'),
                                 'r').read()
        self.assertEqual(new_file_contents, expected1)
