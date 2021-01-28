from dataclasses import dataclass

from .machinery import build_key_machine, build_machine, MaxSizeFinder
from .serdata import encode, decode, clserialize, clkeyhashserialize, clkeyserialize


def cdr(cls):
    cls = dataclass(cls)
    machine = build_machine(cls)
    cls.cdr = machine
    cls.cdrkey = machine
    cls.encode = encode
    cls.decode = classmethod(decode)

    # For dds:
    cls.typename = cls.__name__
    cls.keyless = False
    cls.deserialize = classmethod(decode)
    cls.serialize = classmethod(clserialize)
    cls.key = classmethod(clkeyserialize)
    cls.keyhash = classmethod(clkeyhashserialize)

    finder = MaxSizeFinder()
    cls.cdr.max_size(finder)
    cls.key_max_size = finder.size

    return cls


def keylist(*keys):
    def keyfactory(cls):
        cls.cdrkey = build_key_machine(keys, cls)
        finder = MaxSizeFinder()
        cls.cdrkey.max_size(finder)

        cls.keyless = False
        cls.key_max_size = finder.size

        return cls

    return keyfactory
