#!/usr/bin/env python
"""
Templer
=======

Create files based on templates and the power of [Jinja2](http://jinja.pocoo.org/).

Features:

* templating using Jinja2
* render multiple templates at ones
* render jinja2 context files themselves before using those to render the templates
* use of YAML files as sources of variables

"""

from setuptools import setup, find_packages

setup(
    name='templer',
    version='0.3.1',
    author='Andre Lehmann',
    author_email='aisberg@posteo.de',

    url='',
    license='LGPL',
    description='Create files based on templates and the power of Jinja2.',
    long_description=__doc__,
    keywords=['Jinja2', 'templating', 'command-line', 'CLI'],

    package_dir={ '': 'src' },
    packages=find_packages('src'),
    scripts=[],
    entry_points={
        'console_scripts': [
            'templer = templer:main',
        ]
    },

    install_requires=[
        'jinja2 >= 2.7.2',
        'pyyaml >= 3.0.0',
    ],
    include_package_data=True,
    zip_safe=False,

    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
    ],
)