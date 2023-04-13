#! /usr/bin/env python3
"""Installation script"""

from setuptools import setup

setup(
    name='urlshortener',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='<info@homeinfo.de>',
    maintainer='Richard Neumann',
    maintainer_email='<r.neumann@homeinfo.de>',
    py_modules=['urlshortener'],
    requires=['basex', 'flask', 'peewee', 'peeweeplus', 'wsgilib'],
    license='GPLv3',
    description='URL shortener.'
)
