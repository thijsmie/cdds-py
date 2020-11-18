from inspect import signature
from ctypes import CFUNCTYPE


def c_call(cname):
    """Convert a function into call into the class associated dll"""

    class DllCall:
        def __init__(self, function):
            self.function = function

        # This gets called when the class is finalized
        def __set_name__(self, cls, name):
            s = signature(self.function)

            # Set c function types based on python type annotations
            cfunc = getattr(cls.dll_handle, cname)
            cfunc.restype = s.return_annotation

            # Note: ignoring the 'self' argument
            cfunc.argtypes = [p.annotation for i, p in enumerate(s.parameters.values()) if i > 0]

            # Need to rebuild this function to ignore the 'self' attribute
            def final_func(self, *args):
                return cfunc(*args)

            # replace class named method with c call
            setattr(cls, name, final_func)

    return DllCall


class CCallable:
    def __init__(self, type, function):
        self.type = type
        self.function = function

    def bind(self, fn):
        def bindable(*args):
            try:
                self.function(oself, *args)
            except:
                # Supress all errors to avoid passing them back into C libs
                pass
        return self.type(bindable)


def c_callable(function) -> CFUNCTYPE:
    s = signature(function)

    # make a c func based on python type annotations
    return CFUNCTYPE(s.return_annotation, *[p.annotation for i, p in enumerate(s.parameters.values())])