# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from collections import namedtuple
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError
from ConfigParser import NoSectionError
from io import StringIO
from io import open
import os.path
import requests
from urlparse import urlparse


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
        config = ConfigParser()
        config.readfp(get_data_stream(url))
    try:
        extends = config.get('buildout', 'extends').strip()
    except (NoSectionError, NoOptionError):
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
    for (resource, ref) in resources:
        if is_remote(resource):
            freeze_resource(base_path, resource, cache, ref)
        elif was_remote(resource):
            update_resource(base_path, resource, cache, ref)
    return "Frozen\n"


def freeze_resource(base_path, resource, cache, ref, etag=None):
    frozen_folder = os.path.join(base_path, 'external_buildouts')
    if not os.path.exists(frozen_folder):
        os.makedirs(frozen_folder)
    abs_target_filename, rel_target_filename =\
        frozen_filename(frozen_folder, resource)
    if resource in cache:
        contents = cache[resource]
    else:
        headers = {}
        if etag:
            headers['If-None-Match'] = etag
        response = requests.get(resource, headers=headers)
        contents = response.text
        etag = response.headers.get('etag', None)
        contents = get_data_stream(resource).read()
    prefix = MAINTENANCE_PREFIX.format(etag, resource)
    open(abs_target_filename, 'w').write(prefix + contents)
    if is_remote(ref):
        # The reference was also remote. Doesn't matter. It is guaranteed that
        # it has been frozen before
        ref, _ = frozen_filename(frozen_folder, ref)
    new_data = open(ref).read().replace(resource, rel_target_filename)
    open(ref, 'w').write(new_data)


def update_resource(base_path, resource, cache, ref):
    etag, url = map(lambda line: line.split(':', 1)[1].strip(),
                    open(resource).read().splitlines()[2:4])
    freeze_resource(base_path, url, cache, ref, etag)
