import pytest

from cdds.core import Entity
from cdds.core.exception import DDSException, DDS_RETCODE_UNSUPPORTED
from cdds.domain import DomainParticipant
from cdds.sub import Subscriber


def isgoodentity(v):
    return v != None and \
           isinstance(v, Entity) and \
           hasattr(v, "_ref") and \
           type(v._ref) == int and \
           v._ref > 0


def test_initialize_subscriber():
    dp = DomainParticipant(0)
    sub = Subscriber(dp)

    assert isgoodentity(sub)
