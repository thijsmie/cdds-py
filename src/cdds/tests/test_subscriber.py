import pytest

from cdds.core import Entity
from cdds.core.exception import DDSException, DDS_RETCODE_UNSUPPORTED
from cdds.domain import DomainParticipant
from cdds.sub import Subscriber
from cdds.util.entity import isgoodentity


def test_initialize_subscriber():
    dp = DomainParticipant(0)
    sub = Subscriber(dp)

    assert isgoodentity(sub)
