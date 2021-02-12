#!/usr/bin/env python
import sys
from setuptools import setup, find_packages


if sys.version_info < (3, 6):
    sys.exit("This package cannot be installed in Python version 3.5 or lower.")
elif sys.version_info < (3, 7):
    # We are in any Python 3.6 version
    REQUIRES = ['dataclasses==0.8', 'typing-extensions==3.7.4.3', 'typing-inspect==0.6.0']
elif sys.version_info < (3, 9):
    # We are in any Python 3.7 or 3.8 version
    REQUIRES = ['typing-extensions==3.7.4.3']
else:
    # We are in any Python 3.9 or 3.10 (maybe higher?) version, no requirements
    REQUIRES = []


setup(
    name='pycdr',
    version='0.1.2',
    python_requires=">3.6.9",
    install_requires=REQUIRES,
    description='Python CDR serialization',
    author='Thijs Miedema',
    author_email='thijs.miedema@adlinktech.com',
    packages=find_packages()
)
