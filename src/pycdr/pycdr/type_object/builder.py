from typing_extensions import final
from pycdr.pycdr.types import IdlUnion
from .idl_entities import CompleteStructType, CompleteTypeDetail, CompleteTypeObject, EK_COMPLETE, IS_AUTOID_HASH, IS_NESTED, PlainSequenceSElemDefn, TypeObject, CompleteStructMember, \
    CommonStructMember, CompleteMemberDetail, CompleteStructHeader, PlainSequenceLElemDefn, PlainCollectionHeader, PlainArrayLElemDefn, PlainArraySElemDefn, \
    StringSTypeDefn, StringLTypeDefn, TypeIdentifier, IS_FINAL, IS_APPENDABLE, IS_MUTABLE

from dataclasses import dataclass, fields

from typing import List, Dict, Annotated, get_origin, get_args
from enum import Enum
from pycdr.types import char, wchar, int8, int16, int32, int64, uint8, uint16, uint32, uint64, float32, float64
from pycdr.helper import CDR
from hashlib import md5

from .idl_entities import TK_BOOLEAN, TK_BYTE, TK_INT16, TK_INT32, TK_INT64, TK_UINT16, TK_UINT32, TK_UINT64, TK_FLOAT32, \
    TK_FLOAT64, TK_FLOAT64, TK_CHAR8, TK_CHAR16, TI_STRING8_LARGE
from .util import uint32_max, uint8_max



class TypeObjectBuilder:
    def __init__(self):
        self.type_objects = {}
        self._hash_of = {}

        self.type_dispatch = {
            bool: TK_BOOLEAN,
            char: TK_CHAR8,
            wchar: TK_CHAR16,
            int8: TK_CHAR8,
            int16: TK_INT16,
            int32: TK_INT32,
            int64: TK_INT64,
            uint8: TK_BYTE,
            uint16: TK_UINT16,
            uint32: TK_UINT32,
            uint64: TK_UINT64,
            float32: TK_FLOAT32,
            float64: TK_FLOAT64,
            str: TI_STRING8_LARGE,
            list: (lambda x: self.type_identifier_sequence_of(x, uint32_max)),
            Annotated: (lambda x, a: self.type_identifier_annotated_type(x, a))
        }

    def type_identifier_sequence_of(self, _type, bound):
        if bound <= uint8_max:
            return TypeIdentifier(seq_sdefn=PlainSequenceSElemDefn(
                header=PlainCollectionHeader(
                    equiv_kind=None, # TODO
                    element_flags=0, # TODO
                ),
                bound=bound,
                element_identifier=self.type_identifier_resolve(_type)
            ))
        else:
            return TypeIdentifier(seq_ldefn=PlainSequenceLElemDefn(
                header=PlainCollectionHeader(
                    equiv_kind=None, # TODO
                    element_flags=0, # TODO
                ),
                bound=bound,
                element_identifier=self.type_identifier_resolve(_type)
            ))


    def type_identifier_array_of(self, _type, bound):
        if bound <= uint8_max:
            return TypeIdentifier(array_sdefn=PlainArraySElemDefn(
                header=PlainCollectionHeader(
                    equiv_kind=None, # TODO
                    element_flags=0, # TODO
                ),
                bound=[bound],
                element_identifier=self.type_identifier_resolve(_type)
            ))
        else:
            return TypeIdentifier(array_ldefn=PlainArraySElemDefn(
                header=PlainCollectionHeader(
                    equiv_kind=None, # TODO
                    element_flags=0, # TODO
                ),
                bound=[bound],
                element_identifier=self.type_identifier_resolve(_type)
            ))


    def type_identifier_string(self, bound):
        if bound <= uint8_max:
            return TypeIdentifier(string_sdefn=StringSTypeDefn(bound=bound))
        else:
            return TypeIdentifier(string_ldefn=StringLTypeDefn(bound=bound))


    def type_identifier_annotated_type(self, x, a):
        o = get_origin(x)
        if o == list:
            if a[0] == 'Len':
                return self.type_identifier_array_of(get_args(x)[0], a[1])
            elif a[0] == 'MaxLen':
                return self.type_identifier_sequence_of(get_args(x)[0], a[1])
        if o == str:
            if a[0] == 'MaxLen':
                return self.type_identifier_string(a[1])

        raise Exception("No such type identifier")

    def type_identifier_resolve_complex(self, _type):
        hash = self.hash_of(_type)
        a = TypeIdentifier()
        a.set(EK_COMPLETE, hash)
        return a


    def type_identifier_resolve(self, _type):
        o = get_origin(_type)
        v = self.type_dispatch.get(o)
        if v is None:
            self.type_identifier_resolve_complex(_type)
        elif not callable(v):
            a = TypeIdentifier()
            a.set(v, None)
            return a
        return v(*get_args(_type))

    def register_typeobj(self, datatype, typeobj):
        data = typeobj.serialize()

        f = md5()
        f.update(data)
        hash = f.digest()[:14]

        self.type_objects[hash] = typeobj
        self._hash_of[id(datatype)] = hash

    def hash_of(self, datatype):
        if id(datatype) in self._hash_of:
            return self._hash_of[id(datatype)]
        
        self.to_typeobject(datatype)
        return self._hash_of[id(datatype)]

    def struct_to_typeobject(self, struct):
        members = []
        member_id = 0
        for field in fields(struct):
            members.append(CompleteStructMember(
                common=CommonStructMember(
                    member_id=member_id,
                    member_flags=[],   # TODO
                    member_type_id=self.type_identifier_resolve(field.type)
                ),
                detail=CompleteMemberDetail(
                    member_name=field.name,
                    ann_builtin=None,  # TODO
                    ann_custom=None    # TODO
                )
            ))
            member_id += 1
            
        typeobj = TypeObject(
            complete=CompleteTypeObject(
                struct_type=CompleteStructType(
                    struct_flags=
                        (IS_FINAL if struct.cdr.final else 0) |
                        (IS_MUTABLE if struct.cdr.mutable else 0) |
                        (IS_APPENDABLE if struct.cdr.appendable else 0) |
                        (IS_NESTED if struct.cdr.nested else 0) |
                        (IS_AUTOID_HASH if struct.cdr.autoid_hash else 0),
                    header=CompleteStructHeader(
                        base_type=self.type_identifier_resolve(struct.__base__),
                        detail=CompleteTypeDetail(
                            ann_builtin=None,  # TODO
                            ann_custon=None,   # TODO
                            type_name=struct.typename
                        )
                    ),
                    member_seq=members
                )
            )
        )

        self.register_typeobj(struct, typeobj)
        return typeobj

    def to_typeobject(self, object):
        if isinstance(object, IdlUnion):
            return self.union_to_typeobject(object)
        elif isinstance(object, Enum):
            return self.enum_to_typeobject(object)
        elif isinstance(object, dataclass) and hasattr(object, 'cdr') and isinstance(object.cdr, CDR):
            return self.struct_to_typeobject(object)
        raise Exception("Can't convert object to typeobject")

