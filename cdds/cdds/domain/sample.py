from cdds.internal.clib import load_library, load_library_with_path, MissingLibraryException
from cdds.internal.dds_types import dds_topic_descriptor_p_t
from ctypes import CDLL, Structure, c_int, c_char_p, byref, cast
from dataclasses import dataclass, fields, asdict

from inspect import getabsfile
import os


loaded_libs = {}

def Sample(_lib):
    lib = _lib

    def DDSEntity(clso):
        if lib not in loaded_libs:
            try:
                loaded_libs[lib] = load_library(lib)
            except MissingLibraryException:
                path = os.path.join(os.path.abspath(os.path.dirname(getabsfile(clso))), f"build/lib{lib}.so")
                loaded_libs[lib] = load_library_with_path(lib, path)
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
                return cls(**{f: getattr(struct, f) for (f,_) in Struct._fields_})

            def to_struct(self):
                self.struct = Struct(**asdict(self))
                return byref(self.struct)


        return Sample
    return DDSEntity
