#!/usr/bin/env python
"""
Templer
=======

Render template files with [Jinja2](http://jinja.pocoo.org/). Variables can be passed as command line arguments or defined in a context file.

Features:
* templating using Jinja2
* context files are written in YAML
* use multiple context files to render multiple templates at ones
* render jinja2 context files themselves before using those to render the templates
* easy definition of default values

"""

from setuptools import setup, find_packages

setup(
    name='templer',
    version='0.3.2',
    author='Andre Lehmann',
    author_email='aisberg@posteo.de',

    url='',
    license='LGPL',
    description='Render template files with Jinja2.',
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
