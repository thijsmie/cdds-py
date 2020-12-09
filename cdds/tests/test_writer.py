import pytest

from cdds.core import Entity
from cdds.core.exception import DDSException, DDS_RETCODE_UNSUPPORTED
from cdds.domain import DomainParticipant
from cdds.topic import Topic
from cdds.pub import Publisher, DataWriter

from testtopics import Message

def isgoodentity(v):
    return v != None and \
           isinstance(v, Entity) and \
           hasattr(v, "_ref") and \
           type(v._ref) == int and \
           v._ref > 0


def test_initialize_writer():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, "Message")
    pub = Publisher(dp)
    dw = DataWriter(pub, tp)

    assert isgoodentity(dw)


def test_writeto_writer():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, "Message")
    pub = Publisher(dp)
    dw = DataWriter(pub, tp)

    msg = Message(
        message=b"TestMessage"
    )

    dw.write(msg)