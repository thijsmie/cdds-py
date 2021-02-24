import os
import platform
from ctypes import CDLL


def load_cyclone():
    load_method = ""
    load_path = ""

    if 'CDDS_NO_IMPORT_LIBS' in os.environ:
        return None

    if 'ddsc' in os.environ:
        # library was directly specified in environment variables
        load_method = 'env'
        load_path = [os.environ['ddsc']]
    elif "CYCLONEDDS_HOME" in os.environ and platform.system() == "Linux":
        load_method = 'home'
        load_path = [os.path.join(os.environ["CYCLONEDDS_HOME"], "lib", "libddsc.so")]
    elif "CYCLONEDDS_HOME" in os.environ and platform.system() == "Darwin":
        load_method = 'home'
        load_path = [os.path.join(os.environ["CYCLONEDDS_HOME"], "lib", "libddsc.dylib")]
    elif "CYCLONEDDS_HOME" in os.environ and platform.system() == "Windows":
        load_method = 'home'
        load_path = [os.path.join(os.environ["CYCLONEDDS_HOME"], "bin", "ddsc.dll")]
    elif platform.system() == "Linux":
        load_method = "guess"
        load_path = [os.path.join(p, "libddsc.so") for p in ["", "/usr/lib/", "/usr/local/lib/", "/usr/lib64/", "/lib/", "/lib64/"]]
    elif platform.system() == "Darwin":
        load_method = "guess"
        load_path = [os.path.join(p, "libddsc.dylib") for p in ["", "/usr/lib/", "/usr/local/lib/", "/usr/lib64/", "/lib/", "/lib64/"]]
    else:
        load_method = "guess"
        load_path = ["libddsc.so", "ddsc.dll", "libddsc.dylib"]

    lib = None
    for path in load_path:
        try:
            lib = CDLL(path)
        except OSError:
            continue
        if lib:
            break
    
    if not lib:
        raise Exception(f"Failed to load CycloneDDS with method {load_method} from path(s): {', '.join(load_path)}.")

    return lib
