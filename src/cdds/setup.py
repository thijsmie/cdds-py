#!/usr/bin/env python

from distutils.core import setup

setup(
    name='cdds',
    version='0.1',
    description='Cyclone DDS Python binding',
    author='Thijs Miedema',
    author_email='thijs.miedema@adlinktech.com',
    packages=['cdds'],
    package_dir={'cdds': 'cdds/'},
)
