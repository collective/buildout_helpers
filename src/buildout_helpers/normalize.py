# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from collections import defaultdict

import logging
import re


is_section = re.compile(r'^\[(.*)\]')
is_comment = re.compile(r'^#.*')
is_option = re.compile(r'^(\S+) *[+-=]')
is_nextline_option = re.compile(r'^ +')


logger = logging.getLogger(__name__)
logging.basicConfig()


def parse(stream):
    sections = {'BEFORE_BUILDOUT': {'options': [], 'comments': []}}
    state = 'OPTION/SECTION'
    current_section = sections['BEFORE_BUILDOUT']
    next_comment = []
    current_option = None
    for line in stream:
        if line[-1] != '\n':
            line += '\n'
        if state == 'OPTION/SECTION':
            if is_section.match(line):
                new_section_name = is_section.findall(line)[0]
                assert new_section_name not in sections, \
                    'Section {0} appears more than once'.format(
                        new_section_name)
                sections[new_section_name] = {'options': [], 'comments': []}
                current_section = sections[new_section_name]
                current_section['comments'] = next_comment
                next_comment = []
            elif is_comment.match(line):
                next_comment.append(line)
            elif is_option.match(line):
                name = is_option.findall(line)[0]
                current_option = {'lines': [line], 'comments': next_comment,
                                  'name': name}
                current_section['options'].append(current_option)
                next_comment = []
            elif is_nextline_option.match(line):
                state = 'MULTILINE_OPTION'
                current_option['lines'].extend(next_comment)
                next_comment = []
                current_option['lines'].append(line)
            elif line == '\n':
                continue
            else:
                raise Exception('Did not understand this line: %s',
                                line)
        elif state == 'MULTILINE_OPTION':
            if is_section.match(line):
                new_section_name = is_section.findall(line)[0]
                assert new_section_name not in sections
                sections[new_section_name] = {'options': [], 'comments': []}
                current_section = sections[new_section_name]
                current_section['comments'] = next_comment
                next_comment = []
                state = 'OPTION/SECTION'
            elif is_comment.match(line):
                current_option['lines'].append(line)
            elif is_option.match(line):
                state = 'OPTION/SECTION'
                name = is_option.findall(line)[0]
                current_option = {'lines': [line], 'comments': next_comment,
                                  'name': name}
                current_section['options'].append(current_option)
                next_comment = []
            elif is_nextline_option.match(line):
                current_option['lines'].append(line)
            elif line == '\n':
                state = 'OPTION/SECTION'
            else:
                raise Exception('Did not understand this line: %s',
                                line)

    return sections


def simple_option_handler(option, stream):
    for line in option['comments'] + option['lines']:
        stream.write(line)


def sorted_option_handler(option, stream):
    sortable = option['lines'][1:]
    sortable.sort(key=lambda key: key.lower())
    for line in option['comments'] + option['lines'][0:1]:
        stream.write(line)
    for line in sortable:
        stream.write(line)


option_handlers = defaultdict(lambda: simple_option_handler)
option_handlers['eggs'] = sorted_option_handler
option_handlers['zcml'] = sorted_option_handler
option_handlers['auto-checkout'] = sorted_option_handler


def stream_sorted_options(options, stream):
    def remove_option(name):
        options_to_remove = list(filter(lambda option: option['name'] == name,
                                        options))
        if options_to_remove:
            options.remove(options_to_remove[0])
            return options_to_remove[0]
        return None
    first_option = remove_option('recipe')

    options.sort(key=lambda option: option['lines'][0].lower())

    for option in [first_option] + options:
        if not option:
            continue
        option_handlers[option['name']](option, stream)


def buildout_section_handler(options, stream):
    def remove_option(name):
        options_to_remove = list(filter(lambda option: option['name'] == name,
                                        options))
        if options_to_remove:
            options.remove(options_to_remove[0])
            return options_to_remove[0]
        return None
    first_option = remove_option('recipe')

    options.sort(key=lambda option: option['lines'][0].lower())
    mrdeveloper_keys = ('sources',
                        'sources-dir',
                        'auto-checkout',
                        'always-checkout',
                        'update-git-submodules',
                        'always-accept-server-certificate',
                        'mr.developer-threads',
                        'git-clone-depth')
    mrdeveloper_options = [option for option in options
                           if option['name'] in mrdeveloper_keys]
    options = [option for option in options
               if option['name'] not in mrdeveloper_keys]

    for option in [first_option] + options:
        if not option:
            continue
        option_handlers[option['name']](option, stream)

    if mrdeveloper_options:
        stream.write('\n')

    for option in mrdeveloper_options:
        option_handlers[option['name']](option, stream)


def sources_section_handler(options, stream):
    options.sort(key=lambda x: x['lines'][0].lower())
    longest_name = 0
    longest_repo_type = 0
    longest_url = 0
    longest_args = {}
    all_args = set()
    for option in options:
        name, rest = [x.strip() for x in option['lines'][0].split('=', 1)]
        try:
            repo_type, url, rest = [x.strip() for x in rest.split(' ', 2)]
        except ValueError:
            repo_type, url = [x.strip() for x in rest.split(' ', 1)]
            rest = ''
        args = dict((arg.split('=') for arg in
                     [x.strip() for x in rest.split(' ')] if arg))
        longest_name = max(longest_name, len(name))
        longest_repo_type = max(longest_repo_type, len(repo_type))
        longest_url = max(longest_url, len(url))
        for arg, arg_value in args.items():
            all_args.add(arg)
            longest_args[arg] = max(longest_args.get(arg, 0),
                                    len(arg_value))
        option['name'] = name
        option['repo_type'] = repo_type
        option['url'] = url
        for arg, arg_value in args.items():
            option['arg_{0}'.format(arg)] = arg_value

    all_args = sorted(all_args)
    if 'branch' in all_args:
        all_args.remove('branch')
    for option in options:
        if 'branch' in longest_args:
            arg_string = ''.join(('{arg}={{entry[arg_{arg}]:{len}}} '
                                  .format(arg=arg, len=longest_args[arg])
                                  if 'arg_{0}'.format(arg) in option
                                  else ' ' * (longest_args[arg] + 2 + len(arg))
                                  for arg in ['branch']))
        else:
            arg_string = ''
        arg_string += ''.join(('{arg}={{entry[arg_{arg}]}} '
                               .format(arg=arg)
                               if 'arg_{0}'.format(arg) in option
                               else ''
                               for arg in all_args))
        format_string = ('{comments}{{entry[name]:{longest_name}}} = {{entry[repo_type]:{longest_repo_type}}} {{entry[url]:{longest_url}}} {args:s}\n'  # NOQA
                         .format(args=arg_string,
                                 longest_name=longest_name,
                                 longest_repo_type=longest_repo_type,
                                 longest_url=longest_url,
                                 comments=''.join(option['comments'])))
        stream.write(format_string.format(entry=option).strip() + '\n')


section_handlers = defaultdict(lambda: stream_sorted_options)
section_handlers['buildout'] = buildout_section_handler
section_handlers['sources'] = sources_section_handler


def stream_sorted_sections(sections, stream):
    section_keys = list(sections.keys())
    for special_key in ['buildout', 'versions', 'BEFORE_BUILDOUT', 'sources']:
        if special_key in section_keys:
            section_keys.remove(special_key)
    section_keys.sort(key=lambda key: key.lower())
    section_keys = (['BEFORE_BUILDOUT', 'buildout'] + section_keys +
                    ['sources', 'versions'])
    section_keys = list(filter(lambda key: sections.get(key, None),
                               section_keys))
    for section_key in section_keys:
        section = sections[section_key]
        if section_key != 'BEFORE_BUILDOUT':
            if section_key != section_keys[1]:
                stream.write('\n')
            stream.write('[{0}]\n'.format(section_key))
        stream.write(''.join(section['comments']))
        section_handlers[section_key](section['options'], stream)


def sort(instream, outstream):
    sections = parse(instream)
    stream_sorted_sections(sections, outstream)
