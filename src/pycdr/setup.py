#!/usr/bin/env python

from distutils.core import setup


setup(
    name='pycdr',
    version='0.1',
    description='Python CDR serialization',
    author='Thijs Miedema',
    author_email='thijs.miedema@adlinktech.com',
    packages=['pycdr'],
    package_dir={'pycdr': 'pycdr/'},
#    ext_modules = [module1]
)
