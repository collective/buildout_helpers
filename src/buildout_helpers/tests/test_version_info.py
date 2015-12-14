# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from buildout_helpers.testing import BaseTestCase
from buildout_helpers.version_info import get_version_info

import os.path


class TestVersionInfo(BaseTestCase):
    def test_simple_case(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''\
[buildout]
extends = more_versions.cfg
[versions]
longname = 3
b = 2
a = 2
''')
        self.given_a_file_in_test_dir('more_versions.cfg', '''\
[versions]
longname = 2
''')
        output = get_version_info(cfg).read()
        output = output.replace(os.path.split(cfg)[0], '/wonderland/')
        expected = '''\
a        = \x1b[39m2\x1b[39m 0 /wonderland//buildout.cfg
b        = \x1b[39m2\x1b[39m 0 /wonderland//buildout.cfg
longname = \x1b[39m3\x1b[39m 0 /wonderland//buildout.cfg
         = \x1b[39m2\x1b[39m 1 /wonderland//more_versions.cfg
'''
        self.assertEqual(expected, output)

    def test_color_strange_things(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''\
[buildout]
extends = more_versions.cfg
[versions]
longname = 1
b = 2
a = 2
''')
        self.given_a_file_in_test_dir('more_versions.cfg', '''\
[versions]
longname = 2
''')
        output = get_version_info(cfg).read()
        output = output.replace(os.path.split(cfg)[0], '/wonderland/')
        expected = '''\
a        = \x1b[39m2\x1b[39m 0 /wonderland//buildout.cfg
b        = \x1b[39m2\x1b[39m 0 /wonderland//buildout.cfg
longname = \x1b[31m1\x1b[39m 0 /wonderland//buildout.cfg
         = \x1b[31m2\x1b[39m 1 /wonderland//more_versions.cfg
'''
        self.assertEqual(expected, output)
