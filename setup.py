# -*- coding: utf-8 -*-
# Version 0.1
"""Installer for the collective.normalize_buildout package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='collective.normalize_buildout',
    version='0.3.0',
    description="A buildout config file normalizer",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: BSD License",
    ],
    keywords='Python Plone',
    author='Patrick Gerken',
    author_email='patrick.gerken@zumtobelgroup.com',
    url='http://pypi.python.org/pypi/collective.normalize_buildout',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    extras_require={
        'test': [
        ],
    },
    entry_points="""
[console_scripts]
normalize_buildout = collective.normalize_buildout.cmd:cmd
    """,
)
