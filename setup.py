from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']

setup(
    name='v2gcalendar',
    version=get_version('v2gcalendar/__init__.py'),
    url='http://github.com/felixb/v2gcalendar/',
    license='Apache License, Version 2.0',
    author='Felix Bechstein',
    author_email='f@ub0r.de',
    description='Upload vcalendar files to your Google calendar',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'icalendar',
        'google-api-python-client'
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'mock >= 1.0',
    ],
)
