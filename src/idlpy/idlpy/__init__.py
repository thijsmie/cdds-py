import os
import tempfile
import importlib.util
import subprocess


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


def run_idlc(arg):
    path = os.path.abspath(arg)

    dir = tempfile.mkdtemp()
    proc = subprocess.Popen([idlc, "-l", os.path.join(rundir, "libidlpy.so"), path], cwd=dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        out, err = proc.communicate()
    except subprocess.CalledProcessError:
        print(out)
        print(err)
        import sys
        sys.exit(1)
    return dir


def compile(idl_path):
    dir = run_idlc(idl_path)
    module = os.listdir(dir)[0]
    modpath = os.path.join(dir, module)

    if module.endswith('.py'):
        module = module[:-3]
    
    spec = importlib.util.spec_from_file_location(module, modpath)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    return foo
