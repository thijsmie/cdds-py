"""
 * Copyright(c) 2021 ADLINK Technology Limited and others
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0, or the Eclipse Distribution License
 * v. 1.0 which is available at
 * http://www.eclipse.org/org/documents/edl-v10.php.
 *
 * SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause
"""

from .machinery import build_machine, Buffer, MaxSizeFinder, Endianness
from .type_helper import get_type_hints

from hashlib import md5
from inspect import isclass
from collections import defaultdict
from dataclasses import make_dataclass


def module_prefix(cls):
    cls = cls.__class__ if not isclass(cls) else cls
    module = cls.__module__
    if module is None or module == str.__class__.__module__:
        return ""
    return module + "."


def qualified_name(instance, sep="."):
    cls = instance.__class__ if not isclass(instance) else instance
    return (module_prefix(cls) + cls.__name__).replace('.', sep)


def make_keyholder(datatype, keylist):
    fields = [(k,v) for k,v in get_type_hints(datatype, include_extras=True).items() if k in keylist]
    cls = make_dataclass(qualified_name(datatype) + "KeyHolder", fields)
    cls.cdr = CDR(cls)
    cls.serialize = proto_serialize
    cls.deserialize = classmethod(proto_deserialize)
    return cls


class CDR:
    defined_references = {}
    deferred_references = defaultdict(list)

    def resolve(self, type_name, instance):
        if '.' in qualified_name(self.datatype) and not '.' in type_name:
            # We got a local name, but we only deal in full paths
            type_name = module_prefix(self.datatype) + type_name

        if type_name not in self.defined_references:
            self.deferred_references[type_name].append(instance)
            return None
        return self.defined_references[type_name]

    @classmethod
    def refer(cls, type_name, object):
        for instance in cls.deferred_references[type_name]:
            instance.refer(object)
        del cls.deferred_references[type_name]
        cls.defined_references[type_name] = object

    def __init__(self, datatype, final=True, mutable=False, appendable=False, nested=False, autoid_hash=False, keylist=None):
        self.buffer = Buffer()
        self.datatype = datatype
        self.typename = qualified_name(datatype)
        self.final = final
        self.mutable = mutable
        self.appendable = appendable
        self.nested = nested
        self.autoid_hash = autoid_hash
        self.keylist = keylist

        self.keyholder = make_keyholder(datatype, keylist) if keylist else datatype

        self.machine = build_machine(self, datatype, True)
        self.key_machine = build_machine(self, self.keyholder, True) if keylist else self.machine

        self.keyless = keylist is None

    def finalize(self):
        if not hasattr(self, 'key_max_size'):
            finder = MaxSizeFinder()
            self.key_machine.max_size(finder)
            self.key_max_size = finder.size

    def serialize(self, object, buffer=None, endianness=None) -> bytes:
        buffer = buffer or self.buffer.seek(0)
        if endianness is not None:
            buffer.set_endianness(endianness)

        if buffer.tell() == 0:
            if buffer.endianness == Endianness.Big:
                buffer.write('b', 1, 0)
                buffer.write('b', 1, 0)
                buffer.write('b', 1, 0)
                buffer.write('b', 1, 0)
            else:
                buffer.write('b', 1, 0)
                buffer.write('b', 1, 1)
                buffer.write('b', 1, 0)
                buffer.write('b', 1, 0)

        self.machine.serialize(buffer, object)
        return buffer.asbytes()

    def deserialize(self, data) -> object:
        buffer = Buffer(data) if not isinstance(data, Buffer) else data

        if buffer.tell() == 0:
            buffer.read('b', 1)
            v = buffer.read('b', 1)
            if v == 0:
                buffer.set_endianness(Endianness.Big)
            else:
                buffer.set_endianness(Endianness.Little)
            buffer.read('b', 1)
            buffer.read('b', 1)

        return self.machine.deserialize(buffer)

    def key(self, object) -> bytes:
        self.buffer.seek(0)
        self.buffer.set_endianness(Endianness.Big)
        self.buffer.write('b', 1, 0)
        self.buffer.write('b', 1, 0)
        self.buffer.write('b', 1, 0)
        self.buffer.write('b', 1, 0)

        self.key_machine.serialize(self.buffer, object)
        return self.buffer.asbytes()

    def keyhash(self, object) -> bytes:
        if not hasattr(self, 'key_max_size'):
            self.finalize()

        if self.key_max_size <= 16:
            return self.key(object).ljust(16, b'\0')
        
        m = md5()
        m.update(self.key(object))
        return m.digest()


def proto_serialize(self, buffer=None, endianness=None):
    return self.cdr.serialize(self, buffer=buffer, endianness=endianness)


def proto_deserialize(cls, data):
    return cls.cdr.deserialize(data)
