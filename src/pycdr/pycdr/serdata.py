from hashlib import md5

from .machinery import Buffer


def encode(self, buffer=None):
    buffer = buffer or Buffer()
    self.cdr.encode(buffer, self)
    return buffer.asbytes()


def decode(cls, data=None, buffer=None):
    buffer = buffer or Buffer(data)
    return cls.cdr.decode(buffer)


def serialize(object):
    buffer = Buffer()
    object.cdr.encode(buffer, object)
    return buffer.asbytes()


def deserialize(object, data):
    buffer = Buffer(data)
    obj = object.cdr.decode(buffer)
    return obj


def key_serialize(object):
    buffer = Buffer()
    object.cdrkey.encode(buffer, object)
    return buffer.asbytes()


def key_hash_serialize(object):
    buffer = Buffer()
    object.cdrkey.encode(buffer, object)
    res = buffer.asbytes()
    if object.key_max_size <= 16:
        return res.ljust(16, b'\0')
    m = md5()
    m.update(res)
    return m.digest()


def clserialize(cls, obj):
    buffer = Buffer()
    cls.cdr.encode(buffer, obj)
    return buffer.asbytes()