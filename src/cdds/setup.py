#!/usr/bin/env python

import os
from setuptools import setup, find_packages, Extension


if "CYCLONEDDS_HOME" in os.environ:
    home = os.environ["CYCLONEDDS_HOME"]
    ddspy = Extension('ddspy', 
        sources = ['clayer/src/pysertype.c'], 
        libraries=['ddsc'], 
        include_dirs=[os.path.join(home, "include")],
        library_dirs=[os.path.join(home, "lib"), os.path.join(home, "bin")]
    )
else:
    ddspy = Extension('ddspy', 
        sources = ['clayer/src/pysertype.c'], 
        libraries=['ddsc']
    )

setup(
    name='cdds',
    version='0.1',
    description='Cyclone DDS Python binding',
    author='Thijs Miedema',
    author_email='thijs.miedema@adlinktech.com',
    packages=find_packages(),
	ext_modules = [ddspy]
)