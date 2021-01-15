import pytest

from cdds.core import Entity
from cdds.core.exception import DDSException, DDS_RETCODE_UNSUPPORTED
from cdds.domain import DomainParticipant
from cdds.pub import Publisher
from cdds.util.entity import isgoodentity


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
