from .machinery import build_machine, build_key_machine, Buffer, MaxSizeFinder

from hashlib import md5
from collections import defaultdict



class CDR:
    deferred_references = defaultdict(list)

    @classmethod
    def defer(cls, type_name, instance):
        cls.deferred_references[type_name].append(instance)

    @classmethod
    def refer(cls, type_name, object):
        for instance in cls.deferred_references[type_name]:
            instance.refer(object)
        del cls.deferred_references[type_name]

    def __init__(self, datatype, final=False, mutable=False, appendable=True, nested=False, autoid_hash=False, keylist=None):
        self.buffer = Buffer()
        self.datatype = datatype
        self.typename = datatype.__name__
        self.final = final
        self.mutable = mutable
        self.appendable = appendable
        self.nested = nested
        self.autoid_hash = autoid_hash
        self.keylist = keylist

        self.machine = build_machine(self, datatype, True)
        self.key_machine = build_key_machine(self, keylist, datatype) if keylist else self.machine

        self.keylist = keylist is None

    def serialize(self, object, buffer=None) -> bytes:
        buffer = buffer or self.buffer.seek(0)
        self.machine.serialize(self.buffer, object)
        return self.buffer.asbytes()

    def deserialize(self, data) -> object:
        buffer = Buffer(data)
        return self.machine.deserialize(buffer)

    def key(self, object) -> bytes:
        self.buffer.seek(0)
        self.key_machine.serialize(self.buffer, object)
        return self.buffer.asbytes()

    def keyhash(self, object) -> bytes:
        if not hasattr(self, 'key_max_size'):
            finder = MaxSizeFinder()
            self.key_machine.max_size(finder)
            self.key_max_size = finder.size

        if self.key_max_size <= 16:
            return self.key(object).ljust(16, b'\0')
        
        m = md5()
        m.update(self.key(object))
        return m.digest()


def proto_serialize(self, buffer=None):
    return self.cdr.serialize(self, buffer=buffer)


def proto_deserialize(cls, data):
    return cls.cdr.deserialize(data)