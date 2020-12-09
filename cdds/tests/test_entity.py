import pytest

from cdds.core import Entity
from cdds.domain import DomainParticipant
from cdds.topic import Topic
from cdds.sub import Subscriber, DataReader
from cdds.pub import Publisher, DataWriter
from cdds.core.exception import DDSException, DDS_RETCODE_PRECONDITION_NOT_MET

from testtopics import Message


def isgoodentity(v):
    return v != None and \
           isinstance(v, Entity) and \
           hasattr(v, "_ref") and \
           type(v._ref) == int and \
           v._ref > 0

def test_create_entity():
    dp = DomainParticipant(0)

    assert isgoodentity(dp)


def test_delete_entity():
    dp = DomainParticipant(0)

    assert dp.get_participant() == dp

    reference = dp._ref
    del dp

    with pytest.raises(DDSException) as exc:
        Entity(reference).get_participant()
        
    assert exc.value.code == DDS_RETCODE_PRECONDITION_NOT_MET


def test_get_parent():
    dp = DomainParticipant(0)

    assert dp.get_parent() == dp.parent == None

    tp = Topic(dp, Message, 'Message')

    assert isgoodentity(tp)
    assert tp.parent == tp.get_parent() == dp

    sub = Subscriber(dp)

    assert isgoodentity(sub)
    assert sub.parent == sub.get_parent() == dp

    pub = Publisher(dp)

    assert isgoodentity(pub)
    assert pub.parent == pub.get_parent() == dp

    dr = DataReader(sub, tp)

    assert isgoodentity(dr)
    assert dr.parent == dr.get_parent() == sub

    dw = DataWriter(pub, tp)

    assert isgoodentity(dw)
    assert dw.parent == dw.get_parent() == pub


def test_get_participant():
    dp = DomainParticipant(0)

    assert dp.participant == dp.get_participant() == dp

    tp = Topic(dp, Message, 'Message')

    assert isgoodentity(tp)
    assert tp.participant == tp.get_participant() == dp

    sub = Subscriber(dp)

    assert isgoodentity(sub)
    assert sub.participant == sub.get_participant() == dp

    pub = Publisher(dp)

    assert isgoodentity(pub)
    assert pub.participant == pub.get_participant() == dp

    dr = DataReader(sub, tp)

    assert isgoodentity(dr)
    assert dr.participant == dr.get_participant() == dp

    dw = DataWriter(pub, tp)

    assert isgoodentity(dw)
    assert dw.participant == dw.get_participant() == dp


def test_get_children():
    dp = DomainParticipant(0)

    assert len(dp.children) == len(dp.get_children()) == 0

    tp = Topic(dp, Message, 'Message')

    assert isgoodentity(tp)
    assert len(dp.children) == len(dp.get_children()) == 1
    assert dp.children[0] == dp.get_children()[0] == tp
    assert len(tp.children) == len(tp.get_children()) == 0

    sub = Subscriber(dp)

    assert isgoodentity(sub)
    assert len(dp.children) == len(dp.get_children()) == 2
    assert set(dp.children) == set([sub, tp])
    assert len(sub.children) == len(sub.get_children()) == 0

    pub = Publisher(dp)

    assert isgoodentity(pub)
    assert len(dp.children) == len(dp.get_children()) == 3
    assert set(dp.children) == set([pub, sub, tp])
    assert len(pub.children) == len(pub.get_children()) == 0

    dr = DataReader(sub, tp)

    assert isgoodentity(dr)
    assert set(dp.children) == set([pub, sub, tp])
    assert len(sub.children) == 1
    assert sub.children[0] == dr

    dw = DataWriter(pub, tp)

    assert isgoodentity(dw)
    assert set(dp.children) == set([pub, sub, tp])
    assert len(pub.children) == 1
    assert pub.children[0] == dw

    del dw
    del dr
    del pub
    del sub
    del tp

    assert len(dp.children) == len(dp.get_children()) == 0
