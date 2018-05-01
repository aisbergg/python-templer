#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os import path

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md')) as f:
    long_description = f.read()

setup(
    name='Templer',
    version='1.1.4',
    author='Andre Lehmann',
    author_email='aisberg@posteo.de',
    url='https://github.com/Aisbergg/python-templer',
    license='LGPL',
    description='Render template files with the power of Jinja2.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='Jinja2 templating command-line CLI',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/Aisbergg/python-templer/issues',
        'Source': 'https://github.com/Aisbergg/python-templer',
    },
    packages=find_packages(exclude=['examples']),
    entry_points={
        'console_scripts': [
            'templer = templer:cli',
        ]
    },
    install_requires=[
        'jinja2',
        'pyyaml',
    ],
    include_package_data=True,
    zip_safe=False,
    platforms=['POSIX'],
)
