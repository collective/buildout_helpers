# -*- coding: utf-8 -*-
from StringIO import StringIO
from collective.normalize_buildout.cmd import sort
from collective.normalize_buildout.testing import BaseTestCase


class TestScript(BaseTestCase):

    def test_good_case(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '\n'.join([
            '[buildout]',
            '[bla]',
            'a=1',
            'recipe=xxx',
            '# comment',
            'bla=1',
            '[versions]',
            'a=1',
            '[sources]',
            'xxx = git http:aaa branch=xxx',
            'yyy = git xfdsfdsfsdfsdfdsfdsfsdfdsfsdfdsf branch=yyy'
        ]))
        output = StringIO()

        sort(file(cfg), output)
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

    def test_regression1(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '\n'.join([
            '[sources]',
            '# xxx',
            '# yyy',
            'a = git http...',
        ]))
        output = StringIO()

        sort(file(cfg), output)
        output.seek(0)

        expected = '''[sources]
# xxx
# yyy
a = git http...'''

        self.assertEqual(expected, output.read())

    def test_regression2(self):
        cfg = self.given_a_file_in_test_dir('buildout.cfg', '''
[filter]
extra-field-types =
            <charFilter class="solr.PatternReplaceCharFilterFactory" pattern="(/)+$" replacement=""/>
'''.strip())  # NOQA
        output = StringIO()

        sort(file(cfg), output)
        output.seek(0)

        expected = '''
[filter]
extra-field-types =
            <charFilter class="solr.PatternReplaceCharFilterFactory" pattern="(/)+$" replacement=""/>
'''.strip()  # NOQA

        self.assertEqual(expected, output.read())
