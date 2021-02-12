import os
from inspect import signature
from ctypes import CFUNCTYPE


def c_call(cname):
    """Convert a function into call into the class associated dll"""

    class DllCall:
        def __init__(self, function):
            self.function = function

        # This gets called when the class is finalized
        def __set_name__(self, cls, name):
            if 'CDDS_NO_IMPORT_LIBS' in os.environ:
                return

            s = signature(self.function)

            # Set c function types based on python type annotations
            cfunc = getattr(cls._dll_handle, cname)

            # Note: in python 3.10 we get NoneType for voids instead of None
            # This confuses ctypes a lot, so we explicitly test for it
            cfunc.restype = s.return_annotation if s.return_annotation != type(None) else None

            # Note: ignoring the 'self' argument
            cfunc.argtypes = [p.annotation for i, p in enumerate(s.parameters.values()) if i > 0]

            # Need to rebuild this function to ignore the 'self' attribute
            def final_func(self_, *args):
                return cfunc(*args)

            # replace class named method with c call
            setattr(cls, name, final_func)

    return DllCall


def c_callable(return_type, argument_types) -> CFUNCTYPE:
    # make a c func based on python type annotations
    return CFUNCTYPE(return_type, *argument_types)
