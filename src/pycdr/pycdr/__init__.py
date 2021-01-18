from dataclasses import dataclass

from .machinery import build_key_machine, build_machine, MaxSizeFinder
from .serdata import encode, decode, key_encode


def cdr(cls):
    cls = dataclass(cls)
    machine = build_machine(cls)
    cls.cdr = machine
    cls.encode = encode
    cls.decode = classmethod(decode)
    return cls


def keylist(**keys):
    def keyfactory(cls):
        cls.cdrkey = build_key_machine(keys, cls)
        finder = MaxSizeFinder()
        cls.cdrkey.max_size(finder)

        cls.key_encode = key_encode
        cls.key_max_size = finder.size

        # TODO: add keyhash property
        return cls

    return keyfactory
