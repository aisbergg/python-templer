#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='Templer',
    version='1.0.2',
    author='Andre Lehmann',
    author_email='aisberg@posteo.de',
    url='https://github.com/Aisbergg/python-templer',
    license='LGPL',
    description='Render template files with the power of Jinja2.',
    long_description=long_description,
    keywords=['Jinja2', 'templating', 'command-line', 'CLI'],
    package_dir={ '': 'src' },
    packages=find_packages('src'),
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
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: LGPL License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
