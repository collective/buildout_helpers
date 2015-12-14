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
    if ref_url:
        if not (url.startswith('/') or url.startswith('http')):
            url = '/'.join(ref_url.split('/')[:-1] + [url])
    return url


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
    rel_target_filename = os.path.join('external_buildouts', filename)
    abs_target_filename = os.path.join(frozen_folder, filename)
    return abs_target_filename, rel_target_filename


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
    url = absolutize_url(url, ref_url)
    retval = [(url, ref_url)]
    if url in cache:
        config = cache[url]
    else:
        config = configparser.ConfigParser()
        config.readfp(get_data_stream(url))
    try:
        extends = config.get('buildout', 'extends').strip()
    except (configparser.NoSectionError, configparser.NoOptionError):
        extends = ''
    for extend in (item
                   for line in extends.splitlines()
                   for item in line.split()):
        retval.extend(get_all_resources(extend.strip(), cache, url))
    return retval


def freeze(args):
    url = args.configfile
    cache = {}
    base_path, _ = os.path.split(url)
    resources = get_all_resources(url, cache, url)
    frozen = 0
    refreshed = 0
    for (resource, ref) in resources:
        if is_remote(resource):
            freeze_resource(base_path, resource, cache, ref)
            frozen += 1
        elif was_remote(resource):
            update_resource(base_path, resource, cache, ref)
            refreshed += 1
    return "Froze {} resources, refreshed {} resources\n".format(frozen,
                                                                 refreshed)


def freeze_resource(base_path, resource, cache, ref, etag=None):
    frozen_folder = os.path.join(base_path, 'external_buildouts')
    if not os.path.exists(frozen_folder):
        os.makedirs(frozen_folder)
    abs_target_filename, rel_target_filename =\
        frozen_filename(frozen_folder, resource)
    if resource in cache:
        contents = cache[resource]
        write = True
    else:
        headers = {}
        if etag:
            headers['If-None-Match'] = etag
        response = requests.get(resource, headers=headers)
        write = response.status_code != 304
        contents = response.text
        etag = response.headers.get('etag', None)
    prefix = MAINTENANCE_PREFIX.format(etag, resource)
    if write:
        open(abs_target_filename, 'w').write(prefix + contents)
    if is_remote(ref) or was_remote(ref):
        # The reference was also remote. Doesn't matter. It is guaranteed that
        # it has been frozen before
        # But in this case we must handle relative references too
        rel_resource = relativize_url(resource, ref)
        if is_remote(ref):
            ref, _ = frozen_filename(frozen_folder, ref)
        rel_target_filename = '/'.join(rel_target_filename.split('/')[1:])
        # Prefix replacement strings with empty chars
        # as a hack to prevent overwriting parts of absolute urls
        new_data = open(ref).read().replace(' ' + rel_resource,
                                            ' ' + rel_target_filename)
        open(ref, 'w').write(new_data)
    else:
        ref = ref
    new_data = open(ref).read().replace(resource, rel_target_filename)
    open(ref, 'w').write(new_data)


def update_resource(base_path, resource, cache, ref):
    etag, url = map(lambda line: line.split(':', 1)[1].strip(),
                    open(resource).read().splitlines()[2:4])
    freeze_resource(base_path, url, cache, ref, etag)
