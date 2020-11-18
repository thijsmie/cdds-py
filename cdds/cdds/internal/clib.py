import os
from ctypes import CDLL
from ctypes.util import find_library


class MissingLibraryException(Exception):
    pass


def load_library_with_path(name, path):
    if path is None:
        raise MissingLibraryException(f"No valid path to the required library {name} was found.")
    lib = CDLL(path)
    if lib is None:
        raise MissingLibraryException(f"Failed to load requested library {name} from path {path}.")
    return lib

def load_library(name):
    if name in os.environ:
        # library was specified in environment variables
        return load_library_with_path(name, os.environ[name])
    else:
        return load_library_with_path(name, find_library(name))

