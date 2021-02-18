import os
import sys
import tempfile
import importlib
import subprocess
from importlib.abc import MetaPathFinder


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
bin = cyclone_config('bindir')

rundir = os.path.abspath(os.path.dirname(__file__))
idlc = os.path.join(bin, "idlc")


class IDLException(Exception):
    pass


def run_idlc(arg, dir):
    path = os.path.abspath(arg)

    proc = subprocess.Popen([idlc, "-l", os.path.join(rundir, "libidlpy.so"), path], cwd=dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        out, err = proc.communicate()
    except subprocess.CalledProcessError:
        raise IDLException(out + err)


def compile(idl_path):
    dir = tempfile.mkdtemp()
    run_idlc(idl_path, dir)
    module = os.listdir(dir)[0]

    sys.path.insert(0, dir)

    if module.endswith('.py'):
        module = module[:-3]
    
    module = importlib.import_module(module)
    sys.path.pop(0)
    return module


class JITIDL(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if path is None or path == "":
            path = [os.getcwd()] # top level import -- 

        # We are always only interested in the toplevel module
        if "." in fullname:
            name, *children = fullname.split(".")
        else:
            name = fullname

        loc_idl = None
        for entry in path:
            if os.path.isdir(os.path.join(entry, name)):
                # Found, system can import
                return None
            
            filename_py = os.path.join(entry, name + ".py")
            filename_idl = os.path.join(entry, name + ".idl")

            if os.path.exists(filename_py):
                # Found, system can import
                return None
            
            if os.path.exists(filename_idl):
                # IDL file located
                loc_idl = filename_idl

        if loc_idl:
            # We have found an idl file but we did not find a python module
            dir = os.path.dirname(loc_idl)
            run_idlc(loc_idl, dir)

        # Even if we have compiled the idl module we will let the normal python
        # system handle the import.
        return None 


sys.meta_path.insert(0, JITIDL())