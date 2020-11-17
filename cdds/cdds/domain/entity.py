from cdds.internal.dds_types import dds_topic_descriptor_p_t
from ctypes import CDLL, Structure, c_int, c_char_p, byref, cast
from dataclasses import dataclass, fields, asdict
from ctypes.util import find_library


loaded_libs = {}

def _type_support(cls):
    return cast(cls.dll_handle["dds_" + cls.__name__ + "_desc"], dds_topic_descriptor_p_t)

def _autoconvert(obj):
    return obj.c_struct(**asdict(obj))._ref


def DDSEntity(lib):
    if lib not in loaded_libs:
        library = find_library(lib)
        loaded_libs[lib] = CDLL(library)

    lib = loaded_libs[lib]

    def DDSEntity(clso):
        clso = dataclass(clso)

        class CStyleStruct(Structure, clso):
            _fields_ = [(f.name, f.type) for f in fields(clso)]
            dll_handle = lib
            
            @classmethod
            def type_support(cls):
                return cast(cls.dll_handle["dds_" + clso.__name__ + "_desc"], dds_topic_descriptor_p_t)

            @property
            def _ref(self):
                return byref(self)

        return CStyleStruct
    return DDSEntity
