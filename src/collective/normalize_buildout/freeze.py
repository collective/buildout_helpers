# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from collections import defaultdict
from collections import namedtuple
from collections import OrderedDict
from ConfigParser import ConfigParser
from ConfigParser import NoOptionError
from ConfigParser import NoSectionError
from io import StringIO
from io import open
import colorama
import os.path
import requests
from urlparse import urlparse


VersionInfo = namedtuple("VersionInfo", ("version", "origin"))


def absolutize_url(url, ref_url):
    if ref_url:
        if not (url.startswith('/') or url.startswith('http')):
            url = '/'.join(ref_url.split('/')[:-1] + [url])
    return url


def extract_versions_section(url, ref_url=None):
    versions = OrderedDict(defaultdict(list))

    config = ConfigParser()
    if ref_url:
        if not (url.startswith('/') or url.startswith('http')):
            url = '/'.join(ref_url.split('/')[:-1] + [url])
    if os.path.isfile(url):
        config.read(url)
    else:
        response = requests.get(url).iter_content()
        config.readfp(response)
    # first read own versions section
    if config.has_section('versions'):
        versions.update({pkg_name: [VersionInfo(version, url)]
                         for pkg_name, version in config.items('versions')})
    try:
        extends = config.get('buildout', 'extends').strip()
    except (NoSectionError, NoOptionError):
        return versions
    for extend in extends.splitlines():
        if extend.strip():
            for pkg, version_info in extract_versions_section(extend.strip(),
                                                              url).items():
                versions[pkg].extend(version_info)
    return versions


def get_data_stream(url):
    if is_remote(url):
        data = requests.get(url).text
    else:
        data = open(url).read()
    retval = StringIO()
    retval.write(data)
    retval.seek(0)
    return retval


def freeze(url):
    cache = {}
    base_path, _ = os.path.split(url)
    resources = get_all_resources(url, cache, url)
    for (resource, ref) in resources:
        if is_remote(resource):
            freeze_resource(base_path, resource, cache, ref)


def is_remote(resource):
    return not os.path.isfile(resource)


def frozen_filename(frozen_folder, url):
    components = urlparse(url)
    filename = '{components.netloc}_{path}'.format(
        components=components,
        path='_'.join(components.path[1:].split('/')))
    rel_target_filename = os.path.join('external_buildouts', filename)
    abs_target_filename = os.path.join(frozen_folder, filename)
    return abs_target_filename, rel_target_filename


def freeze_resource(base_path, resource, cache, ref):
    frozen_folder = os.path.join(base_path, 'external_buildouts')
    if not os.path.exists(frozen_folder):
        os.makedirs(frozen_folder)
    abs_target_filename, rel_target_filename =\
        frozen_filename(frozen_folder, resource)
    if resource in cache:
        contents = cache[resource]
    else:
        response = requests.get(resource)
        contents = response.text
        etag = response.headers.get('etag', None)
        contents = get_data_stream(resource).read()
    prefix = '''\
# File managed by freeze command from collective.normalize_buildout
# Changes will be overwritten
# ETAG: {}
'''.format(etag)
    open(abs_target_filename, 'w').write(prefix + contents)
    if is_remote(ref):
        # The reference was also remote. Doesn't matter. It is guaranteed that
        # it has been frozen before
        ref, _ = frozen_filename(frozen_folder, ref)
    new_data = open(ref).read().replace(resource, rel_target_filename)
    open(ref, 'w').write(new_data)


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
    for extend in extends.splitlines():
        retval.extend(get_all_resources(extend.strip(), cache, url))
    return retval


def get_version_info(url):
    out_stream = StringIO()
    pkg_maxlen = 0
    version_maxlen = 0

    version_sections = extract_versions_section(url)
    for pkg_name, version_infos in version_sections.items():
        pkg_maxlen = max(len(pkg_name), pkg_maxlen)
        for version_info in version_infos:
            version_maxlen = max(version_info.version, version_maxlen)

    outfmt = ('{{pkg_name:{pkg_maxlen}}} = {{color}}{{version_info.version:{version_maxlen}}}{reset} {{index}} {{version_info.origin}}\n'  # NOQA
              .format(pkg_maxlen=pkg_maxlen, version_maxlen=version_maxlen,
                      reset=colorama.Fore.RESET))

    for pkg_name, version_infos in version_sections.items():
        if (max((version_info['version'] for version_info in version_infos)) !=
                version_infos[0]['version']):
            color = colorama.Fore.RED
        else:
            color = colorama.Fore.RESET
        for index, version_info in enumerate(version_infos):
            pkg_name_to_show = pkg_name if not index else ''
            out_stream.write(outfmt.format(pkg_name=pkg_name_to_show,
                                           color=color,
                                           version_info=version_info,
                                           index=index))
    out_stream.seek(0)
    return out_stream
