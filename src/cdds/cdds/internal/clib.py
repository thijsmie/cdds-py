import os
import platform
import subprocess
from ctypes import CDLL


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


def load_cyclone():
    load_method = ""
    load_path = ""

    if 'CDDS_NO_IMPORT_LIBS' in os.environ:
        return None

    if 'ddsc' in os.environ:
        # library was specified in environment variables
        load_method = 'env'
        load_path = [os.environ['ddsc']]
    elif platform.system() == "Windows":
        bindir = cyclone_config('bindir')
        if bindir:
            # cyclone-config returned binary dir
            load_method = "cyclone-config"
            load_path = [os.path.join(bindir, "ddsc.dll")]
        else:
            # No cyclone-config binary dir, hope the dll is on windows path
            load_method = "guess"
            load_path = ["ddsc.dll"]
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        libdir = cyclone_config('libdir')
        if libdir:
            # cyclone-config returned binary dir
            load_method = "cyclone-config"
            load_path = [os.path.join(libdir, "libddsc.so")]
        else:
            # No cyclone-config binary dir, hope the dll is in guessed directories
            load_method = "guess"
            load_path = [os.path.join(p, "libddsc.so") for p in ["", "/usr/lib/", "/usr/local/lib/", "/usr/lib64/", "/lib/", "/lib64/"]]
    else:
        # All bets are off, we better just hope the lib is loadable
        load_method = "AllBetsAreOff"
        load_path = ["libddsc.so"]

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
