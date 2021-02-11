from dataclasses import dataclass

from .helper import CDR, proto_deserialize, proto_serialize


def cdr(*args, final=False, mutable=False, appendable=True, keylist=None):
    def cdr(cls):
        cls = dataclass(cls)
        cls.cdr = CDR(cls, final, mutable, appendable, keylist)
        cls.serialize = proto_serialize
        cls.deserialize = classmethod(proto_deserialize)

        return cls

    if args:
        return cdr(args[0])
    return cdr
