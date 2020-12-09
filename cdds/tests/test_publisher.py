import pytest

from cdds.core import Entity
from cdds.core.exception import DDSException, DDS_RETCODE_UNSUPPORTED
from cdds.domain import DomainParticipant
from cdds.pub import Publisher


def isgoodentity(v):
    return v != None and \
           isinstance(v, Entity) and \
           hasattr(v, "_ref") and \
           type(v._ref) == int and \
           v._ref > 0


def test_initialize_publisher():
    dp = DomainParticipant(0)
    pub = Publisher(dp)

    assert isgoodentity(pub)


def test_suspension():
    dp = DomainParticipant(0)
    pub = Publisher(dp)

    with pytest.raises(DDSException) as exc:
        pub.suspend()
    assert exc.value.code == DDS_RETCODE_UNSUPPORTED

    with pytest.raises(DDSException) as exc:
        pub.resume()
    assert exc.value.code == DDS_RETCODE_UNSUPPORTED
