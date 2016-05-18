#! /usr/bin/env python

""" templer main file """
import pkg_resources

__author__ = "Andre Lehmann"
__email__ = "aisberg@posteo.de"
__version__ = pkg_resources.get_distribution('templer').version

from templer.cli import main

if __name__ == '__main__':
    main()
