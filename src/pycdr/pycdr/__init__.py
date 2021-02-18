from dataclasses import dataclass

from .main import CDR, proto_deserialize, proto_serialize


def cdr(*args, final=True, mutable=False, appendable=False, keylist=None):
    def cdr(cls):
        cls = dataclass(cls)
        cls.cdr = CDR(cls, final, mutable, appendable, keylist)
        cls.serialize = proto_serialize
        cls.deserialize = classmethod(proto_deserialize)

        CDR.refer(cls.cdr.typename, cls)

        return cls

    if args:
        return cdr(args[0])
    return cdr
