#!/usr/bin/env python

from distutils.core import setup, Extension


ddspy = Extension('ddspy', sources = ['clayer/src/pysertype.c'], extra_link_args=["-lddsc"], extra_compile_args=["-O0", "-g"])


setup(
    name='cdds',
    version='0.1',
    description='Cyclone DDS Python binding',
    author='Thijs Miedema',
    author_email='thijs.miedema@adlinktech.com',
    packages=['cdds', 'cdds.internal', 'cdds.core', 'cdds.domain', 'cdds.pub', 'cdds.sub', 'cdds.topic', 'cdds.util'],
    package_dir={'cdds': 'cdds/'},
	ext_modules = [ddspy]
)