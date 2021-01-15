# For your own reference and others, go to https://www.omg.org/spec/DDS-XTypes/1.3/Beta1/PDF, page 237, "Interoperability of Keyed Topics"
from .machinery import build_key_machine


def keylist(**keys):
    def keyfactory(cls):
        cls.cdrkey = build_key_machine