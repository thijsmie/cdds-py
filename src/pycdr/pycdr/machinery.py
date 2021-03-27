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

from dataclasses import dataclass, is_dataclass
from enum import Enum, IntEnum, auto
from typing import Union
import struct
import sys
from inspect import isclass

from .types import ArrayHolder, BoundStringHolder, SequenceHolder, default, primitive_types, IdlUnion, NoneType
from .type_helper import Annotated, get_origin, get_args, get_type_hints


class CdrKeyVMOpType(IntEnum):
    Done = 0
    StreamStatic = 1
    Stream2ByteSize = 2
    Stream4ByteSize = 3
    ByteSwap = 4
    RepeatStatic = 5
    Repeat2ByteSize = 6
    Repeat4ByteSize = 7
    EndRepeat = 8
    Union1Byte = 9
    Union2Byte = 10
    Union4Byte = 11
    Union8Byte = 12
    Jump = 13


@dataclass
class CdrKeyVmOp:
    type: CdrKeyVMOpType
    skip: bool
    size: int = 0
    value: int = 0
    align: int = 0


class Endianness(Enum):
    Little = auto()
    Big = auto()

    @staticmethod
    def native():
        return Endianness.Little if sys.byteorder == "little" else Endianness.Big


class Buffer:
    def __init__(self, bytes=None, align_offset=0):
        self._bytes = bytearray(bytes) if bytes else bytearray(512)
        self._pos = 0
        self._size = len(self._bytes)
        self._endian = '='
        self._align_offset = align_offset
        self.endianness = Endianness.native()

    def set_endianness(self, endianness):
        self.endianness = endianness
        if self.endianness == Endianness.Little:
            self._endian = "<"
        else:
            self._endian = ">"

    def zero_out(self):
        # As per testing (https://stackoverflow.com/questions/19671145)
        # Quickest way to zero is to re-alloc..
        self._bytes = bytearray(self._size)

    def set_align_offset(self, offset):
        self._align_offset = offset

    def seek(self, pos):
        self._pos = pos
        return self

    def tell(self):
        return self._pos

    def ensure_size(self, size):
        if self._pos + size > self._size:
            old_bytes = self._bytes
            old_size = self._size
            self._size *= 2
            self._bytes = bytearray(self._size)
            self._bytes[0:old_size] = old_bytes

    def align(self, alignment):
        self._pos = ((self._pos - self._align_offset + alignment - 1) & ~(alignment - 1)) + self._align_offset
        return self

    def write(self, pack, size, value):
        self.ensure_size(size)
        struct.pack_into(self._endian + pack, self._bytes, self._pos, value)
        self._pos += size
        return self

    def write_bytes(self, bytes):
        length = len(bytes)
        self.ensure_size(length)
        self._bytes[self._pos:self._pos+length] = bytes
        self._pos += length
        return self

    def read_bytes(self, length):
        b = bytes(self._bytes[self._pos:self._pos+length])
        self._pos += length
        return b

    def read(self, pack, size):
        v = struct.unpack_from(self._endian + pack, buffer=self._bytes, offset=self._pos)
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
    """Given a type, serialize and deserialize"""
    def __init__(self, type):
        self.alignment = 1
    
    def serialize(self, buffer, value):
        pass

    def deserialize(self, buffer):
        pass

    def max_size(self, finder):
        pass

    def cdr_key_machine_op(self, skip):
        pass


class NoneMachine(Machine):
    def __init__(self):
        self.alignment = 1
    
    def serialize(self, buffer, value):
        pass

    def deserialize(self, buffer):
        pass

    def max_size(self, finder):
        pass

    def cdr_key_machine_op(self, skip):
        return []


class PrimitiveMachine(Machine):
    def __init__(self, type):
        self.type = type
        self.alignment, self.code = primitive_types[self.type]

    def serialize(self, buffer, value):
        buffer.align(self.alignment)
        buffer.write(self.code, self.alignment, value)

    def deserialize(self, buffer):
        buffer.align(self.alignment)
        return buffer.read(self.code, self.alignment)

    def max_size(self, finder: MaxSizeFinder):
        finder.increase(self.alignment, self.alignment)

    def cdr_key_machine_op(self, skip):
        stream = [CdrKeyVmOp(CdrKeyVMOpType.StreamStatic, skip, self.alignment, align=self.alignment)]
        if not skip and not self.alignment == 1:
            stream += [CdrKeyVmOp(CdrKeyVMOpType.ByteSwap, skip, align=self.alignment)]
        return stream


class StringMachine(Machine):
    def __init__(self, bound=None):
        self.alignment = 4
        self.bound = bound

    def serialize(self, buffer, value):
        if self.bound and len(value) > self.bound:
            raise Exception("String longer than bound.")
        buffer.align(4)
        bytes = value.encode('utf-8')
        buffer.write('I', 4, len(bytes) + 1)
        buffer.write_bytes(bytes)
        buffer.write('b', 1, 0)

    def deserialize(self, buffer):
        buffer.align(4)
        numbytes = buffer.read('I', 4)
        bytes = buffer.read_bytes(numbytes - 1)
        buffer.read('b', 1)
        return bytes.decode('utf-8')

    def max_size(self, finder: MaxSizeFinder):
        if self.bound:
            finder.increase(self.bound + 5, 2)  # string size + length serialized (4) + null byte (1)
        else:
            finder.increase(2**64 - 1 + 5, 2)
    
    def cdr_key_machine_op(self, skip):
        return [CdrKeyVmOp(CdrKeyVMOpType.Stream4ByteSize, skip, 1, align=1)]


class BytesMachine(Machine):
    def __init__(self, bound=None):
        self.alignment = 2
        self.bound = bound

    def serialize(self, buffer, value):
        if self.bound and len(value) > self.bound:
            raise Exception("Bytes longer than bound.")
        buffer.align(2)
        buffer.write('H', 2, len(value))
        buffer.write_bytes(value)

    def deserialize(self, buffer):
        buffer.align(2)
        numbytes = buffer.read('H', 2)
        return buffer.read_bytes(numbytes)

    def max_size(self, finder: MaxSizeFinder):
        if self.bound:
            finder.increase(self.bound + 3, 2)  # string size + length serialized (2)
        else:
            finder.increase(65535 + 3, 2)
    
    def cdr_key_machine_op(self, skip):
        return [CdrKeyVmOp(CdrKeyVMOpType.Stream4ByteSize, skip, 1, align=1)]


class ByteArrayMachine(Machine):
    def __init__(self, size):
        self.alignment = 1
        self.size = size

    def serialize(self, buffer, value):
        if self.bound and len(value) != self.size:
            raise Exception("Incorrectly sized array.")

        buffer.write_bytes(value)

    def deserialize(self, buffer):
        return buffer.read_bytes(self.size)

    def max_size(self, finder: MaxSizeFinder):
        finder.increase(self.size, 1)

    def cdr_key_machine_op(self, skip):
        return [CdrKeyVmOp(CdrKeyVMOpType.StreamStatic, skip, self.size, align=1)]
        


class ArrayMachine(Machine):
    def __init__(self, submachine, size):
        self.size = size
        self.submachine = submachine
        self.alignment = submachine.alignment

    def serialize(self, buffer, value):
        assert len(value) == self.size

        for v in value:
            self.submachine.serialize(buffer, v)

    def deserialize(self, buffer):
        return [self.submachine.deserialize(buffer) for i in range(self.size)]

    def max_size(self, finder: MaxSizeFinder):
        if self.size == 0:
            return

        finder.align(self.alignment)
        pre_size = finder.size
        self.submachine.max_size(finder)
        post_size = finder.size

        size = post_size - pre_size
        size = (size + self.alignment - 1) & ~(self.alignment - 1)
        finder.size = pre_size + self.size * size

    def cdr_key_machine_op(self, skip):
        if isinstance(self.submachine, PrimitiveMachine):
            stream = [CdrKeyVmOp(CdrKeyVMOpType.StreamStatic, skip, self.submachine.alignment * self.size, align=self.submachine.alignment)]
            if not skip and self.submachine.alignment != 1:
                stream += [CdrKeyVmOp(CdrKeyVMOpType.ByteSwap, skip, align=self.submachine.alignment)]
            return stream

        subops = self.submachine.cdr_key_machine_op(skip)
        return [CdrKeyVmOp(CdrKeyVMOpType.RepeatStatic, skip, self.size, value=len(subops)+2)] + \
                subops + [CdrKeyVmOp(CdrKeyVMOpType.EndRepeat, skip, len(subops))]


class SequenceMachine(Machine):
    def __init__(self, submachine, maxlen=None):
        self.submachine = submachine
        self.alignment = 2
        self.maxlen = maxlen

    def serialize(self, buffer, value):
        if self.maxlen is not None:
            assert len(value) <= self.maxlen

        buffer.align(2)
        buffer.write('H', 2, len(value))

        for v in value:
            self.submachine.serialize(buffer, v)

    def deserialize(self, buffer):
        buffer.align(2)
        num = buffer.read('H', 2)
        return [self.submachine.deserialize(buffer) for i in range(num)]

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

    def cdr_key_machine_op(self, skip):
        if isinstance(self.submachine, PrimitiveMachine):
            stream = [CdrKeyVmOp(CdrKeyVMOpType.Stream2ByteSize, skip, self.submachine.alignment, align=self.submachine.alignment)]
            if not skip and self.submachine.alignment != 1:
                stream += [CdrKeyVmOp(CdrKeyVMOpType.ByteSwap, skip, align=self.submachine.alignment)]
            return stream

        subops = self.submachine.cdr_key_machine_op(skip)
        return [CdrKeyVmOp(CdrKeyVMOpType.Repeat2ByteSize, skip, value=len(subops)+2)] + \
                subops + [CdrKeyVmOp(CdrKeyVMOpType.EndRepeat, skip, len(subops))]


class UnionMachine(Machine):
    def __init__(self, type, discriminator_machine, labels_submachines, default=None):
        self.type = type
        self.labels_submachines = labels_submachines
        self.alignment = max(s.alignment for s in labels_submachines.values())
        self.alignment = max(self.alignment, discriminator_machine.alignment)
        self.discriminator = discriminator_machine
        self.default = default

    def serialize(self, buffer, union):
        try:
            if union.discriminator is None:
                self.discriminator.serialize(buffer, union._default_val)
                self.default.serialize(buffer, union.value)
            else:
                self.discriminator.serialize(buffer, union.discriminator)
                self.labels_submachines[union.discriminator].serialize(buffer, union.value)
        except Exception as e:
            raise Exception(f"Failed to encode union, {self.type}, value is {union.value}") from e

    def deserialize(self, buffer):
        label = self.discriminator.deserialize(buffer)

        if label not in self.labels_submachines:
            contents = self.default.deserialize(buffer)
        else:
            contents = self.labels_submachines[label].deserialize(buffer)

        return self.type(discriminator=label, value=contents)

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

    def cdr_key_machine_op(self, skip):
        headers = []
        opsets = []
        union_type = {
            1: CdrKeyVMOpType.Union1Byte,
            2: CdrKeyVMOpType.Union2Byte,
            4: CdrKeyVMOpType.Union4Byte,
            8: CdrKeyVMOpType.Union8Byte
        }[self.discriminator.alignment]

        buffer = Buffer(bytes=self.discriminator.alignment)

        for label, submachine in self.labels_submachines.items():
            buffer.seek(0)
            self.discriminator.serialize(buffer, label)
            buffer.seek(0)
            value = buffer.read({1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[self.discriminator.alignment], self.discriminator.alignment)
            headers.append(CdrKeyVmOp(union_type, skip, value=value))
            opsets.append(submachine.cdr_key_machine_op(skip))

        lens = [len(o) + 2 for o in opsets]

        if self.default is not None:
            opsets.append(self.discriminator.cdr_key_machine_op(skip) + self.default.cdr_key_machine_op(skip))
            lens.append(len(opsets[-1]))
        else:
            lens[-1] -= 1

        jumps = [sum(lens[i:]) for i in range(len(lens))]

        for i in range(len(headers)):
            if i != len(opsets)-1:
                opsets[i].append(CdrKeyVmOp(CdrKeyVMOpType.Jump, skip, size=jumps[i+1]+1))
            headers[i].size = lens[i]
            opsets[i] = [headers[i]] + opsets[i]

        return sum(opsets, [])



class MappingMachine(Machine):
    def __init__(self, key_machine, value_machine):
        self.key_machine = key_machine
        self.value_machine = value_machine
        self.alignment = 2

    def serialize(self, buffer, values):
        buffer.align(2)
        buffer.write('H', 2, len(values))

        for key, value in values.items():
            self.key_machine.serialize(buffer, key)
            self.value_machine.serialize(buffer, value)

    def deserialize(self, buffer):
        ret = {}
        buffer.align(2)
        num = buffer.read('H', 2)

        for i in range(num):
            key = self.key_machine.deserialize(buffer)
            value = self.value_machine.deserialize(buffer)
            ret[key] = value

        return ret

    def max_size(self, finder: MaxSizeFinder):
        finder.increase(2, 2)

        pre_size = finder.size
        self.key_machine.max_size(finder)
        self.value_machine.max_size(finder)
        post_size = finder.size

        finder.size = pre_size + (post_size - pre_size) * 65535

    def cdr_key_machine_op(self, skip):
        raise NotImplementedError()


class StructMachine(Machine):
    def __init__(self, object, members_machines):
        self.type = object
        self.members_machines = members_machines

    def serialize(self, buffer, value):
        #  We use the fact here that dicts retain their insertion order
        #  This is guaranteed from python 3.7 but no existing python 3.6 implementation
        #  breaks this guarantee.

        for member, machine in self.members_machines.items():
            try:
                machine.serialize(buffer, getattr(value, member))
            except Exception as e:
                raise Exception(f"Failed to encode member {member}, value is {getattr(value, member)}") from e

    def deserialize(self, buffer):
        valuedict = {}
        for member, machine in self.members_machines.items():
            valuedict[member] = machine.deserialize(buffer)
        return self.type(**valuedict)

    def max_size(self, finder):
        for k, m in self.members_machines.items():
            m.max_size(finder)

    def cdr_key_machine_op(self, skip):
        return sum((m.cdr_key_machine_op(skip) for m in self.members_machines.values()), [])

    def cdr_key_machine_with_keylist(self, keylist):
        return sum((m.cdr_key_machine_op(name not in keylist) for name, m in self.members_machines.items()), [])



class InstanceMachine(Machine):
    def __init__(self, object):
        self.type = object
        self.alignment = 1

    def serialize(self, buffer, value):
        if value is None:
            print(f"Skipping the {self.type} object for now.")
            return
        return value.serialize(buffer)

    def deserialize(self, buffer):
        return self.type.deserialize(buffer)

    def max_size(self, finder):
        self.type.cdr.machine.max_size(finder)

    def cdr_key_machine_op(self, skip):
        return self.type.cdr.machine.cdr_key_machine_op(skip)


class DeferredInstanceMachine(Machine):
    def __init__(self, object_type_name, cdr):
        self.alignment = 1
        self.object_type_name = object_type_name
        self.type = cdr.resolve(object_type_name, self)

    def refer(self, type):
        self.type = type

    def serialize(self, buffer, value):
        return value.serialize(buffer)

    def deserialize(self, buffer):
        if not self.type:
            raise TypeError(f"Deferred type {self.object_type_name} was never defined.")
        return self.type.deserialize(buffer)

    def max_size(self, finder):
        if not self.type:
            raise TypeError(f"Deferred type {self.object_type_name} was never defined.")
        self.type.cdr.machine.max_size(finder)

    def cdr_key_machine_op(self, skip):
        return self.type.cdr.machine.cdr_key_machine_op(skip)


class EnumMachine(Machine):
    def __init__(self, enum):
        self.enum = enum
    
    def serialize(self, buffer, value):
        buffer.write("I", 4, int(value))

    def deserialize(self, buffer):
        return self.enum(buffer.read("I", 4))

    def max_size(self, finder: MaxSizeFinder):
        finder.increase(4, 4)
    
    def cdr_key_machine_op(self, skip):
        stream = [CdrKeyVmOp(CdrKeyVMOpType.StreamStatic, skip, 4, align=4)]
        if not skip:
            stream += [CdrKeyVmOp(CdrKeyVMOpType.ByteSwap, skip, align=4)]
        return stream


def build_machine(cdr, _type, top=False) -> Machine:
    if type(_type) == str:
        return DeferredInstanceMachine(_type, cdr)
    if _type == str:
        return StringMachine()
    elif _type in primitive_types:
        return PrimitiveMachine(_type)
    elif _type == bytes:
        return BytesMachine()
    elif _type == NoneType:
        return NoneMachine()
    elif get_origin(_type) == Annotated:
        args = get_args(_type)
        if len(args) >= 2:
            holder = args[1]
            if type(holder) == tuple:
                # Edge case for python 3.6: bug in backport? TODO: investigate and report
                holder = holder[0]
            if isinstance(holder, ArrayHolder):
                return ArrayMachine(
                    build_machine(cdr, holder.type),
                    size=holder.length
                )
            elif isinstance(holder, SequenceHolder):
                return SequenceMachine(
                    build_machine(cdr, holder.type),
                    maxlen=holder.max_length
                )
            elif isinstance(holder, BoundStringHolder):
                return StringMachine(
                    bound=holder.max_length
                )
    elif get_origin(_type) == Union and len(get_args(_type)) == 2 and get_args(_type)[1] == NoneType:
        # TODO
        return build_machine(cdr, get_args(_type)[0])
    elif get_origin(_type) == list:
        return SequenceMachine(
            build_machine(cdr, get_args(_type)[0])
        )
    elif get_origin(_type) == dict:
        return MappingMachine(
            build_machine(cdr, get_args(_type)[0]),
            build_machine(cdr, get_args(_type)[1])
        )
    elif isclass(_type) and issubclass(_type, IdlUnion):
        return UnionMachine(
            _type,
            build_machine(cdr, _type._discriminator),
            {dv: build_machine(cdr, tp) for dv, (_, tp) in _type._cases.items()},
            default=build_machine(cdr, _type._default[1]) if _type._default else None
        )
    elif isclass(_type) and issubclass(_type, Enum):
        return EnumMachine(_type)
    elif isclass(_type) and is_dataclass(_type) and top:
        _fields = get_type_hints(_type, include_extras=True)
        _members = {k: build_machine(cdr, v) for k, v in _fields.items()}
        return StructMachine(_type, _members)
    elif isclass(_type) and is_dataclass(_type) and hasattr(_type, 'cdr'):
        return InstanceMachine(_type)

    raise TypeError(f"{repr(_type)} is not valid in CDR classes because it cannot be encoded.")
