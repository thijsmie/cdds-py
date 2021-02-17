#!/usr/bin/env python

import os
import subprocess
from setuptools import setup, find_packages


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


prefix = cyclone_config('prefix')
rundir = os.path.abspath(os.path.dirname(__file__))
builddir = os.path.join(rundir, "build")

if not os.path.exists(os.path.join(rundir, "idlpy/libidlpy.so")):
    subprocess.check_call(["mkdir", "-p", builddir])
    subprocess.check_call(["cmake", rundir, f"-DCMAKE_PREFIX_PATH={prefix}"], cwd=builddir)
    subprocess.check_call(["cmake", "--build", "."], cwd=builddir)
    subprocess.check_call(["cp", os.path.join(builddir, "lib/libidlpy.so"), os.path.join(rundir, "idlpy")])


setup(
    name='idlpy',
    version='0.1',
    description='Cyclone DDS Python IDL',
    author='Thijs Miedema',
    author_email='thijs.miedema@adlinktech.com',
    packages=find_packages(),
	include_package_data=True
)