import os
import sys
import platform
from ctypes import CDLL
from ctypes.util import find_library


def load_library_with_path(name, path):
    if path is None:
        return None

    if platform.system() == "Linux":
        # On linux we have potential trouble, because find_library does not return the full path
        # We will try several prefixes
        for prefix in ["", "/usr/lib/", "/usr/local/lib/", "/usr/lib64/", "/lib/", "/lib64/"]:
            try:
                lib = CDLL(prefix + path)
            except OSError:
                continue
            return lib

        # Shame, could not find it
        print("Could not locate CycloneDDS. Set appropriate environment variables or hardcode the path with 'export cdds=/path/to/libddsc.so.'", file=sys.stderr)
        sys.exit(1)
    
    return CDLL(path)


def load_library(name):
    if 'CDDS_NO_IMPORT_LIBS' in os.environ:
        return None

    if name in os.environ:
        # library was specified in environment variables
        return load_library_with_path(name, os.environ[name])
    else:
        return load_library_with_path(name, find_library(name))
