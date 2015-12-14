# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from collections import namedtuple
from io import StringIO
from io import open
import os.path
import requests

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

VersionInfo = namedtuple("VersionInfo", ("version", "origin"))


MAINTENANCE_PREFIX = '''\
# File managed by freeze command from buildout_helpers
# Changes will be overwritten
# ETAG: {}
# ORIGIN: {}
'''


def is_remote(resource):
    return not os.path.isfile(resource)


def was_remote(resource):
    data = open(resource).read().splitlines()
    return data[0:1] == MAINTENANCE_PREFIX.splitlines()[0:1]


def absolutize_url(url, ref_url):
    if url.startswith('http'):
        return url
    elif ref_url.startswith('http'):
        start_path = ref_url.rsplit('/', 1)[0]
        return '/'.join((start_path, url))
    start_path = os.path.split(ref_url)[0]
    target_path = os.path.join(start_path, url)
    return os.path.realpath(target_path)


def relativize_url(url, ref_url):
    url_tokens = url.split('/')
    ref_url_tokens = ref_url.split('/')
    if url_tokens[:3] != ref_url_tokens[:3]:
        return url
    for i in range(3, min(len(url_tokens), len(ref_url_tokens))):
        if url_tokens[i] != ref_url_tokens[i]:
            return '/'.join(url_tokens[i:])


def frozen_filename(frozen_folder, url):
    components = urlparse(url)
    filename = '{components.netloc}_{path}'.format(
        components=components,
        path='_'.join(components.path[1:].split('/')))
    abs_target_filename = os.path.join(frozen_folder, filename)
    return abs_target_filename


def get_data_stream(url):
    if is_remote(url):
        data = requests.get(url).text
    else:
        data = open(url).read()
    retval = StringIO()
    retval.write(data)
    retval.seek(0)
    return retval


def get_all_resources(url, cache, ref_url):
    abs_url = absolutize_url(url, ref_url)
    retval = [(abs_url, url, ref_url)]
    if abs_url in cache:
        config = cache[abs_url]
    else:
        config = configparser.ConfigParser()
        config.readfp(get_data_stream(abs_url))
    try:
        extends = config.get('buildout', 'extends').strip()
    except (configparser.NoSectionError, configparser.NoOptionError):
        extends = ''
    for extend in (item
                   for line in extends.splitlines()
                   for item in line.split()):
        retval.extend(get_all_resources(extend.strip(), cache, abs_url))
    return retval


def freeze(args):
    url = args.configfile
    cache = {}
    base_path, _ = os.path.split(url)
    resources = get_all_resources(url, cache, url)
    frozen = 0
    refreshed = 0
    for (abs_resource, rel_resource, ref) in resources:
        if is_remote(abs_resource):
            freeze_resource(base_path, abs_resource, rel_resource, cache, ref)
            frozen += 1
        elif was_remote(abs_resource):
            update_resource(base_path, abs_resource, rel_resource, cache, ref)
            refreshed += 1
    return "Froze {} resources, refreshed {} resources\n".format(frozen,
                                                                 refreshed)


def create_replacement_url(referencing_file, new_file):
    ref_file_abs = os.path.realpath(referencing_file)
    ref_folder_abs = os.path.split(ref_file_abs)[0]
    new_file_abs = os.path.realpath(new_file)
    new_rel_path = os.path.relpath(new_file_abs, ref_folder_abs)
    return new_rel_path


def freeze_resource(base_path, abs_resource, rel_resource,
                    cache, ref, etag=None):
    frozen_folder = os.path.join(base_path, 'external_buildouts')
    if not os.path.exists(frozen_folder):
        os.makedirs(frozen_folder)
    abs_target_filename = frozen_filename(frozen_folder, abs_resource)
    if abs_resource in cache:
        contents = cache[abs_resource]
        write = True
    else:
        headers = {}
        if etag:
            headers['If-None-Match'] = etag
        response = requests.get(abs_resource, headers=headers)
        write = response.status_code != 304
        contents = response.text
        etag = response.headers.get('etag', None)
    prefix = MAINTENANCE_PREFIX.format(etag, abs_resource)
    if write:
        open(abs_target_filename, 'w').write(prefix + contents)
    if is_remote(ref):
        ref = frozen_filename(frozen_folder, ref)
    rel_target_filename = create_replacement_url(ref, abs_target_filename)
    new_data = open(ref).read().replace(rel_resource, rel_target_filename)
    open(ref, 'w').write(new_data)


def update_resource(base_path, abs_resource, rel_resource, cache, ref):
    etag, url = map(lambda line: line.split(':', 1)[1].strip(),
                    open(abs_resource).read().splitlines()[2:4])
    freeze_resource(base_path, url, rel_resource, cache, ref, etag)
