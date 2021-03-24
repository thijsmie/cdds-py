
[![codecov](https://codecov.io/gh/thijsmie/cdds-py/branch/master/graph/badge.svg?token=BL8314M28L)](https://codecov.io/gh/thijsmie/cdds-py)
[![License](https://img.shields.io/badge/License-EPL%202.0-blue)](https://choosealicense.com/licenses/epl-2.0/)
[![License](https://img.shields.io/badge/License-EDL%201.0-blue)](https://choosealicense.com/licenses/edl-1.0/)

# Cyclone DDS Python

Work in progress on the CycloneDDS Python API.

## Getting started 

First, get a python and pip installation of a sufficiently high version (3.6+). Next, you'll need to have CycloneDDS installed on your system. Set a CYCLONEDDS_HOME environment variable to your installation directory. You can then install pycdr and cyclonedds as contained in this repo:

```bash
$ cd src
$ pip install ./pycdr
$ pip install ./cyclonedds
```

If you get permission errors you are using your system python. This is not recommended, please use a [virtualenv](https://docs.python.org/3/tutorial/venv.html) or use something like pipenv/pyenv/poetry.

You can now run examples or work in an interactive notebook with jupyter:

```bash
$ pip install jupyterlab
$ jupyter-lab
```
