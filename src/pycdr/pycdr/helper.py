from .machinery import build_machine, build_key_machine, Buffer, MaxSizeFinder

from hashlib import md5



class CDR:
    def __init__(self, datatype, final=False, mutable=False, appendable=True, nested=False, autoid_hash=False, keylist=None):
        self.buffer = Buffer()
        self.datatype = datatype
        self.final = final
        self.mutable = mutable
        self.appendable = appendable
        self.nested = nested
        self.autoid_hash = autoid_hash
        self.keylist = keylist

        self.machine = build_machine(datatype)
        self.key_machine = build_key_machine(keylist, datatype) if keylist else self.machine

        finder = MaxSizeFinder()
        self.key_machine.max_size(finder)
        self.key_max_size = finder.size

    def serialize(self, object) -> bytes:
        self.buffer.seek(0)
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
        if self.key_max_size <= 16:
            return self.key(object).ljust(16, b'\0')
        
        m = md5()
        m.update(self.key(object))
        return m.digest()

    @property
    def keyless(self):
        return self.keylist is None


def proto_serialize(self):
    return self.cdr.serialize(self)


def proto_deserialize(cls, data):
    return cls.cdr.deserialize(data)