# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from buildout_helpers.normalize import sort
from buildout_helpers.testing import BaseTestCase
from io import open
from io import StringIO


class TestNormalize(BaseTestCase):

    def test_good_case(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''\
[buildout]
[bla]
a=1
recipe=xxx
# comment
bla=1
[versions]
a=1
[sources]
xxx = git http:aaa branch=xxx
yyy = git xfdsfdsfsdfsdfdsfdsfsdfdsfsdfdsf branch=yyy
''')
        output = StringIO()

        sort(open(cfg), output)
        output.seek(0)

        expected = '''[buildout]

[bla]
recipe=xxx
a=1
# comment
bla=1

[sources]
xxx = git http:aaa                         branch=xxx
yyy = git xfdsfdsfsdfsdfdsfdsfsdfdsfsdfdsf branch=yyy

[versions]
a=1
'''

        self.assertEqual(expected, output.read())

    def test_versions_and_sources_last(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''\
[buildout]
[versions]
[sources]
[www]
[zzz]
[aaa]''')
        output = StringIO()
        sort(open(cfg), output)
        output.seek(0)

        expected = '''\
[buildout]

[aaa]

[www]

[zzz]

[sources]

[versions]
'''

        self.assertEqual(expected, output.read())

    def test_mrdev_options_grouped(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''\
[buildout]
sources = sources
bla = 1
auto-checkout = *''')
        output = StringIO()

        sort(open(cfg), output)
        output.seek(0)

        expected = '''[buildout]
bla = 1

auto-checkout = *
sources = sources
'''

        self.assertEqual(expected, output.read())

    def test_regression1(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''
[sources]
# xxx
# yyy
a = git http...''')
        output = StringIO()

        sort(open(cfg), output)
        output.seek(0)

        expected = '''[sources]
# xxx
# yyy
a = git http...
'''

        self.assertEqual(expected, output.read())

    def test_regression2(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''
[filter]
extra-field-types =
            <charFilter class="solr.PatternReplaceCharFilterFactory" pattern="(/)+$" replacement=""/>
''')  # NOQA
        output = StringIO()

        sort(open(cfg), output)
        output.seek(0)

        expected = '''\
[filter]
extra-field-types =
            <charFilter class="solr.PatternReplaceCharFilterFactory" pattern="(/)+$" replacement=""/>
'''  # NOQA

        self.assertEqual(expected, output.read())

    def test_regression3(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''
[filter]
extra-field-types =
 <charFilter class="solr.PatternReplaceCharFilterFactory" pattern="(/)+$" replacement=""/>
''')  # NOQA
        output = StringIO()

        sort(open(cfg), output)
        output.seek(0)

        expected = '''\
[filter]
extra-field-types =
 <charFilter class="solr.PatternReplaceCharFilterFactory" pattern="(/)+$" replacement=""/>
'''  # NOQA

        self.assertEqual(expected, output.read())
