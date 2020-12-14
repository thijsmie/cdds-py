from cdds.internal.clib import load_library, load_library_with_path
from cdds.internal.dds_types import dds_topic_descriptor_p_t
from ctypes import Structure, c_char_p, byref, cast, string_at
from dataclasses import dataclass, fields, asdict

from inspect import getabsfile
import os
from copy import copy as cp


loaded_libs = {}


def copy(v, t):
    if t == c_char_p:
        v = cp(string_at(v))
        print(v.decode())
    return v


def Sample(_lib):
    lib = _lib

    def DDSEntity(clso):
        if lib not in loaded_libs:
            loaded_libs[lib] = load_library(lib)
            if loaded_libs[lib] == None:
                path = os.path.join(os.path.abspath(os.path.dirname(getabsfile(clso))), f"build/lib{lib}.so")
                loaded_libs[lib] = load_library_with_path(lib, path)
            if loaded_libs[lib] == None:
                raise Exception(f"The library this entity belongs to could not be loaded. Please ensure {lib} is available.")
        mlib = loaded_libs[lib]

        clso = dataclass(clso)
        cls_type_support = cast(mlib["dds_" + clso.__name__ + "_desc"], dds_topic_descriptor_p_t)

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
                return cls(**{f: copy(getattr(struct, f), t) for (f, t) in Struct._fields_})

            def to_struct(self):
                self.struct = Struct(**asdict(self))
                return byref(self.struct)

        return Sample
    return DDSEntity
