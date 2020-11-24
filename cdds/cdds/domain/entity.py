from cdds.internal import load_library
from cdds.internal.dds_types import dds_topic_descriptor_p_t
from ctypes import CDLL, Structure, c_int, c_char_p, byref, cast
from dataclasses import dataclass, fields, asdict



loaded_libs = {}

def _type_support(cls):
    return cast(cls.dll_handle["dds_" + cls.__name__ + "_desc"], dds_topic_descriptor_p_t)

def _autoconvert(obj):
    return obj.c_struct(**asdict(obj))._ref


def Sample(lib):
    if lib not in loaded_libs:
        loaded_libs[lib] = load_library(lib)
    lib = loaded_libs[lib]

    def DDSEntity(clso):
        clso = dataclass(clso)
        cls_type_support = cast(lib["dds_" + clso.__name__ + "_desc"], dds_topic_descriptor_p_t)

        class Struct(Structure):
            _fields_ = [(f.name, f.type) for f in fields(clso)]

        class Sample(clso):
            type_support = cls_type_support
            struct_class = Struct
            
            def __init__(self, *args, **kwargs) -> None:
                self.struct = None
                super().__init__(*args, **kwargs)

            @classmethod
            def from_struct(cls, struct):
                return cls(**{f: getattr(struct, f) for (f,_) in Struct._fields_})

            def to_struct(self):
                self.struct = Struct(**asdict(self))
                return byref(self.struct)


        return Sample
    return DDSEntity
