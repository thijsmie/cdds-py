from cdds.core import Entity


def isgoodentity(v):
    return v != None and \
           isinstance(v, Entity) and \
           hasattr(v, "_ref") and \
           type(v._ref) == int and \
           v._ref > 0
