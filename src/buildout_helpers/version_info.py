# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from collections import namedtuple
from collections import OrderedDict
from io import StringIO
from pkg_resources import parse_version
import colorama
import os.path
import requests
try:
    import ConfigParser as configparser
except ImportError:
    import configparser


VersionInfo = namedtuple("VersionInfo", ("version", "origin"))


def extract_versions_section(url, ref_url=None):
    versions = OrderedDict()

    config = configparser.ConfigParser()
    if ref_url:
        if not (url.startswith('/') or url.startswith('http')):
            url = '/'.join(ref_url.split('/')[:-1] + [url])
    if os.path.isfile(url):
        config.read(url)
    else:
        response = requests.get(url)
        config.read(response.text)
    # first read own versions section
    if config.has_section('versions'):
        versions.update({pkg_name: [VersionInfo(version, url)]
                         for pkg_name, version in
                         sorted(config.items('versions'))})
    try:
        extends = config.get('buildout', 'extends').strip()
    except (configparser.NoSectionError, configparser.NoOptionError):
        return versions
    for extend in (item
                   for line in extends.splitlines()
                   for item in line.split()):
        if extend.strip():
            for pkg, version_info in extract_versions_section(extend.strip(),
                                                              url).items():
                if pkg not in versions:
                    versions[pkg] = []
                versions[pkg].extend(version_info)
    return versions


def get_version_info(url):
    out_stream = StringIO()
    pkg_maxlen = 0
    version_maxlen = 0

    version_sections = extract_versions_section(url)
    for pkg_name, version_infos in version_sections.items():
        pkg_maxlen = max(len(pkg_name), pkg_maxlen)
        for version_info in version_infos:
            version_maxlen = max(len(version_info.version), version_maxlen)

    outfmt = ('{{pkg_name:{pkg_maxlen}}} = {{color}}{{version_info.version:{version_maxlen}}}{reset} {{index}} {{version_info.origin}}\n'  # NOQA
              .format(pkg_maxlen=pkg_maxlen, version_maxlen=version_maxlen,
                      reset=colorama.Fore.RESET))

    for pkg_name, version_infos in sorted(version_sections.items()):
        if (max((parse_version(version_info.version)
                 for version_info in version_infos)) !=
                parse_version(version_infos[0].version)):
            color = colorama.Fore.RED
        else:
            color = colorama.Fore.RESET
        for index, version_info in enumerate(version_infos):
            pkg_name_to_show = pkg_name if not index else ''
            out_stream.write(outfmt.format(pkg_name=pkg_name_to_show,
                                           version_info=version_info,
                                           color=color,
                                           index=index))
    out_stream.seek(0)
    return out_stream
