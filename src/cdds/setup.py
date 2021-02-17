#!/usr/bin/env python

import subprocess
from setuptools import setup, find_packages, Extension


def cyclone_config(arg, default=None):
    proc = subprocess.Popen(["cyclone-config", f"--{arg}"], stdout=subprocess.PIPE)
    try:
        out, _ = proc.communicate(timeout=0.5)
        if out:
            return out.decode()
        return default
    except subprocess.TimeoutExpired:
        proc.kill()
    return default


include_dir = cyclone_config('includedir')
library_dir = cyclone_config('libdir')

ddspy = Extension('ddspy', 
    sources = ['clayer/src/pysertype.c'], 
    libraries=['ddsc'], 
    include_dirs=[include_dir] if include_dir else None,
    library_dirs=[library_dir] if library_dir else None
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