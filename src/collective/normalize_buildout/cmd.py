# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from argparse import ArgumentParser
from collective.normalize_buildout.normalize import sort
from collective.normalize_buildout.version_info import get_version_info
from io import open
from io import StringIO

import fileinput
import logging
import sys


logger = logging.getLogger(__name__)


def normalize_cmd():
    parser = ArgumentParser()
    parser.add_argument(
        '-c',
        '--check',
        dest='check',
        action='store_true',
        default=False,
        help=('Do not modify buildout file, '
              'only return if file would be modified'))
    parser.add_argument('configfile',
                        help=('The configfile to normalize in place, '
                              'or "-" to read the config file from stdin '
                              'and return the result to stdout'))
    args = parser.parse_args()

    if args.configfile == '-':
        instream = StringIO()
        instream.write(sys.stdin.read())
        instream.seek(0)
        pipe = True
    else:
        instream = open(args.configfile, encoding='utf-8')
        pipe = False
    outstream = StringIO()
    try:
        sort(instream, outstream)
    except Exception:
        logger.exception('Could not parse file')
        return sys.exit(1)
    else:
        instream.seek(0)
        outstream.seek(0)
        changed = instream.read() != outstream.read()
        outstream.seek(0)
        if not changed:
            if pipe:
                sys.stdout.write(outstream.read())
            sys.exit(0)
        else:
            if args.check:
                logger.error('File is not normalized')
                sys.exit(1)
            else:
                if pipe:
                    sys.stdout.write(outstream.read())
                else:
                    open(args.configfile, 'w',
                         encoding='utf-8').write(outstream.read())


def version_info_cmd():
    parser = ArgumentParser(
        description="Print info about pinned versions and its overrides"
    )
    parser.add_argument('configfile',
                        help=('config file to parse'))

    args = parser.parse_args()
    print(get_version_info(args.configfile).read())

if __name__ == '__main__':
    sys.exit(sort(fileinput.input()))
