from cdds.core import Entity


def isgoodentity(v):
    return v is not None and \
           isinstance(v, Entity) and \
           hasattr(v, "_ref") and \
           type(v._ref) == int and \
           v._ref > 0
