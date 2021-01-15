from dataclasses import fields, is_dataclass
from typing import Annotated, List, Union, Mapping, get_origin, get_args
import struct
from .types import (default, char, wchar, int8, int16, int32, int64, uint8, uint16, uint32, uint64,
                    float32, float64, MaxLen, Len, IdlUnion)


primitive_types = {
    char: (1, 'b'),
    wchar: (2, 'h'),
    int8: (1, 'b'),
    int16: (2, 'h'),
    int32: (4, 'i'),
    int64: (8, 'q'),
    uint8: (1, 'B'),
    uint16: (2, 'H'),
    uint32: (4, 'I'),
    uint64: (8, 'Q'),
    float32: (4, 'f'),
    float64: (8, 'd'),
    int: (8, 'q'),
    bool: (1, '?'),
    float: (8, 'd')
}


class Buffer:
    def __init__(self, bytes=None):
        self._bytes = bytearray(bytes) if bytes else bytearray(512)
        self._pos = 0
        self._size = len(self._bytes)
        self._alignc = '@'

    def ensure_size(self, size):
        if self._pos + size < self._size:
            old_bytes = self._bytes
            old_size = self._size
            self._size *= 2
            self._bytes = bytearray(self._size)
            self._bytes[0:old_size] = old_bytes

    def align(self, alignment):
        self._pos = (self._pos + alignment - 1) & ~(alignment - 1)

    def write(self, pack, size, value):
        self.ensure_size(size)
        struct.pack_into(self._alignc + pack, self._bytes, self._pos, value)
        self._pos += size

    def write_bytes(self, bytes):
        l = len(bytes)
        self.ensure_size(l)
        self._bytes[self._pos:self._pos+l] = bytes
        self._pos += l

    def read_bytes(self, length):
        b = bytes(self._bytes[self._pos:self._pos+length])
        self._pos += length
        return b

    def read(self, pack, size):
        v = struct.unpack_from(self._alignc + pack, buffer=self._bytes, offset=self._pos)
        self._pos += size
        return v[0]

    def asbytes(self):
        return bytes(self._bytes[0:self._pos])


class MaxSizeFinder:
    def __init__(self):
        self.size = 0

    def align(self, alignment):
        self.size = (self.size + alignment - 1) & ~(alignment - 1)

    def increase(self, bytes, alignment):
        self.align(alignment)
        self.size += bytes


class Machine:
    """Given a type, encode and decode"""
    def __init__(self, type):
        self.alignment = 1
    
    def encode(self, buffer, value):
        pass

    def decode(self, buffer):
        pass

    def max_size(self, finder):
        pass


class PrimitiveMachine(Machine):
    def __init__(self, type):
        self.type = type
        self.alignment, self.code = primitive_types[self.type]

    def encode(self, buffer, value):
        buffer.align(self.alignment)
        buffer.write(self.code, self.alignment, value)

    def decode(self, buffer):
        buffer.align(self.alignment)
        return buffer.read(self.code, self.alignment)

    def max_size(self, finder: MaxSizeFinder):
        finder.increase(self.alignment, self.alignment)


class StringMachine(Machine):
    def __init__(self, bound=None):
        self.alignment = 4
        self.bound = bound

    def encode(self, buffer, value):
        if self.bound and len(value) > self.bound:
            raise Exception("String longer than bound.")
        buffer.align(4)
        bytes = value.encode('utf-8')
        buffer.write('I', 4, len(bytes) + 1)
        buffer.write_bytes(bytes)
        buffer.write('b', 1, 0)

    def decode(self, buffer):
        buffer.align(4)
        numbytes = buffer.read('I', 4)
        bytes = buffer.read_bytes(numbytes - 1)
        buffer.read('b', 1)
        return bytes.decode('utf-8')

    def max_size(self, finder: MaxSizeFinder):
        if self.bound:
            finder.increase(self.bound + 5, 2)  # string size + length encoded (4) + null byte (1)
        else:
            finder.increase(2**64 - 1 + 5, 2)


class BytesMachine(Machine):
    def __init__(self, bound=None):
        self.alignment = 2
        self.bound = bound

    def encode(self, buffer, value):
        if self.bound and len(value) > self.bound:
            raise Exception("Bytes longer than bound.")
        buffer.align(2)
        buffer.write('H', 2, len(value))
        buffer.write_bytes(value)

    def decode(self, buffer):
        buffer.align(2)
        numbytes = buffer.read('H', 2)
        return buffer.read_bytes(numbytes)

    def max_size(self, finder: MaxSizeFinder):
        if self.bound:
            finder.increase(self.bound + 3, 2)  # string size + length encoded (2)
        else:
            finder.increase(65535 + 3, 2)


class ByteArrayMachine(Machine):
    def __init__(self, size):
        self.alignment = 1
        self.size = size

    def encode(self, buffer, value):
        if self.bound and len(value) != self.size:
            raise Exception("Incorrectly sized array.")

        buffer.write_bytes(value)

    def decode(self, buffer):
        return buffer.read_bytes(self.size)

    def max_size(self, finder: MaxSizeFinder):
        finder.increase(self.size, 1)


class ArrayMachine(Machine):
    def __init__(self, num, submachine):
        self.num = num
        self.submachine = submachine
        self.alignment = submachine.alignment

    def encode(self, buffer, value):
        assert len(value) == self.num

        for v in value:
            self.submachine.encode(buffer, v)

    def decode(self, buffer):
        return [self.submachine.decode(buffer) for i in range(self.num)]

    def max_size(self, finder: MaxSizeFinder):
        if self.num == 0:
            return

        finder.align(self.alignment)
        pre_size = finder.size
        self.submachine.max_size(finder)
        post_size = finder.size

        size = post_size - pre_size
        size = (size + self.alignment - 1) & ~(self.alignment - 1)
        finder.size = pre_size + self.num * size


class SequenceMachine(Machine):
    def __init__(self, submachine, maxlen=None):
        self.submachine = submachine
        self.alignment = 2
        self.maxlen = maxlen

    def encode(self, buffer, value):
        if self.maxlen is not None:
            assert len(value) <= self.maxlen

        buffer.align(2)
        buffer.write('H', 2, len(value))

        for v in value:
            self.submachine.encode(buffer, v)

    def decode(self, buffer):
        buffer.align(2)
        num = buffer.read('H', 2)
        return [self.submachine.decode(buffer) for i in range(num)]

    def max_size(self, finder: MaxSizeFinder):
        if self.maxlen == 0:
            return

        finder.align(self.alignment)
        pre_size = finder.size
        self.submachine.max_size(finder)
        post_size = finder.size

        size = post_size - pre_size
        size = (size + self.alignment - 1) & ~(self.alignment - 1)
        finder.size = pre_size + (self.maxlen if self.maxlen else 65535) * size + 2


class UnionMachine(Machine):
    def __init__(self, discriminator_machine, labels_submachines, default=None):
        self.labels_submachines = labels_submachines
        self.alignment = max(s.alignment for s in labels_submachines.values())
        self.alignment = max(self.alignment, discriminator_machine.alignment)
        self.discriminator = discriminator_machine
        self.default = default

    def encode(self, buffer, value):
        label, contents = value

        self.disciminator.encode(buffer, label)

        if self.default is not None and label not in self.labels_submachines:
            self.default.encode(buffer, label)
        else:
            self.labels_submachines[label].encode(buffer, contents)

    def decode(self, buffer):
        label = self.disciminator.decode(buffer)

        if self.default is not None and label not in self.labels_submachines:
            contents = self.default.decode(buffer)
        else:
            contents = self.labels_submachines[label].decode(buffer)

        return label, contents

    def max_size(self, finder: MaxSizeFinder):
        self.discriminator.max_size(finder)
        pre_size = finder.size
        sizes = []
        
        for submachine in self.labels_submachines.values():
            finder.size = pre_size
            submachine.max_size(finder)
            sizes.append(finder.size - pre_size)
        
        if default:
            finder.size = pre_size
            default.max_size(finder)
            sizes.append(finder.size - pre_size)

        finder.size = pre_size + max(sizes)


class MappingMachine(Machine):
    def __init__(self, key_machine, value_machine):
        self.key_machine = key_machine
        self.value_machine = value_machine
        self.alignment = 2

    def encode(self, buffer, values):
        buffer.align(2)
        buffer.write('H', 2, len(values))

        for key, value in values.items():
            self.key_machine.encode(buffer, key)
            self.value_machine.encode(buffer, value)

    def decode(self, buffer):
        ret = {}
        num = buffer.read('H', 2)

        for i in range(num):
            key = self.key_machine.decode(buffer)
            value = self.value_machine.decode(buffer)
            ret[key] = value

        return ret

    def max_size(self, finder: MaxSizeFinder):
        finder.increase(2, 2)

        pre_size = finder.size
        self.key_machine.max_size(finder)
        self.value_machine.max_size(finder)
        post_size = finder.size

        finder.size = pre_size + (post_size - pre_size) * 65535


class StructMachine(Machine):
    def __init__(self, object, members_machines):
        self.type = object
        self.members_machines = members_machines

    def encode(self, buffer, value):
        #  We use the fact here that dicts retain their insertion order
        #  This is guaranteed from python 3.7 but no existing python 3.6 implementation
        #  breaks this guarantee.

        for member, machine in self.members_machines.items():
            machine.encode(buffer, getattr(value, member))

    def decode(self, buffer):
        valuedict = {}
        for member, machine in self.members_machines.items():
            valuedict[member] = machine.decode(buffer)
        return self.type(**valuedict)

    def max_size(self, finder):
        for m in self.members_machines:
            m.max_size(finder)


def build_machine(_type):
    if _type == str:
        return StringMachine()
    elif _type in primitive_types:
        return PrimitiveMachine(_type)
    elif _type == bytes:
        return BytesMachine()
    elif get_origin(_type) == Annotated:
        args = get_args(_type)
        if get_origin(args[0]) == bytes and type(args[1]) == tuple and len(args[1]) == 2 and args[1][0] == 'MaxLen':
            return BytesMachine(bound=args[1][1])
        elif get_origin(args[0]) == bytes and type(args[1]) == tuple and len(args[1]) == 2 and args[1][0] == 'MaxLen':
            return ByteArrayMachine(length=args[1][1])
        elif get_origin(args[0]) == list and type(args[1]) == tuple and len(args[1]) == 2 and args[1][0] == 'Len':
            return ArrayMachine(
                args[1][1],
                build_machine(get_args(args[0])[0])
            )
        elif get_origin(args[0]) == list and type(args[1]) == tuple and len(args[1]) == 2 and args[1][0] == 'MaxLen':
            return SequenceMachine(
                build_machine(get_args(args[0])[0]),
                maxlen=args[1][1]
            )
    elif get_origin(_type) == list:
        return SequenceMachine(
            build_machine(get_args(_type)[0])
        )
    elif get_origin(_type) == dict:
        return MappingMachine(
            build_machine(get_args(_type)[0]),
            build_machine(get_args(_type)[1])
        )
    elif isinstance(_type, IdlUnion):
        return UnionMachine(
            build_machine(_type._discriminator),
            [build_machine(c) for c in _type._cases],
            default=build_machine(_type._default) if _type._default else None
        )
    elif is_dataclass(_type):
        _fields = fields(_type)
        _members = { f.name: build_machine(f.type) for f in _fields }
        return StructMachine(_type, _members)

    raise Exception(f"Could not make encoding machinery for type {_type}.")


def build_key_machine(keys, cls):
    _fields = fields(cls)
    _members = { f.name: build_machine(f.type) for f in _fields if f.name in keys}
    return StructMachine(cls, _members)