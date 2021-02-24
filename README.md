# cdds-py
[![codecov](https://codecov.io/gh/thijsmie/cdds-py/branch/master/graph/badge.svg?token=BL8314M28L)](https://codecov.io/gh/thijsmie/cdds-py)

Work in progress on the Python Cyclone DDS API.


## Getting started 

First, get a python and pip installation of a sufficiently high version (3.6+). Next, you'll need to have CycloneDDS installed on your system. Set a CYCLONEDDS_HOME environment variable to your installation directory. You can then install PyCDR and CDDS as contained in this repo:

```bash
$ cd src
$ pip install ./pycdr
$ pip install ./cdds
```

If you get permission errors you are using your system python. This is not recommended, please use a [virtualenv](https://docs.python.org/3/tutorial/venv.html) or use something like pipenv/pyenv/poetry.

You can now run examples or work in an interactive notebook with jupyter:

```bash
$ pip install jupyterlab
$ jupyter-lab
```
