import os
from ctypes import CDLL
from ctypes.util import find_library


def load_library_with_path(name, path):
    if path is None:
        return None
    lib = CDLL(path)
    return lib


def load_library(name):
    if 'CDDS_NO_IMPORT_LIBS' in os.environ:
        return None

    if name in os.environ:
        # library was specified in environment variables
        return load_library_with_path(name, os.environ[name])
    else:
        return load_library_with_path(name, find_library(name))
