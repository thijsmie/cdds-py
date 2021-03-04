import pytest

from cyclonedds.domain import DomainParticipant
from cyclonedds.sub import Subscriber
from cyclonedds.util import isgoodentity
from cyclonedds.builtin import BuiltinDataReader, BuiltinTopicDcpsParticipant, BuiltinTopicDcpsSubscription



def test_builtin_dcps_participant():
    dp = DomainParticipant(0)
    sub = Subscriber(dp)
    dr1 = BuiltinDataReader(sub, BuiltinTopicDcpsParticipant)
    dr2 = BuiltinDataReader(sub, BuiltinTopicDcpsSubscription)

    assert isgoodentity(dr1)
    assert isgoodentity(dr2)
    assert dr1.take()[0].key == dp.guid
    msg = dr2.take(N=2)
    assert [msg[0].key, msg[1].key] == [dr1.guid, dr2.guid] or \
           [msg[0].key, msg[1].key] == [dr2.guid, dr1.guid]

    