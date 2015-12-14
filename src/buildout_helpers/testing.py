# -*- coding: utf-8 -*-
from shutil import rmtree
from tempfile import mkdtemp

import os
import unittest


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.realpath(mkdtemp())
        self.options = {
            'bin-directory': 'bin',
            'directory': self.test_dir,
            'jenkins': 'False',
        }

    def tearDown(self):
        rmtree(self.test_dir)

    def given_a_file_in_test_dir(self, filename, contents):
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, 'w') as a_file:
            a_file.write(contents)

        return file_path
