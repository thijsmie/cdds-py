import pytest

from cyclonedds.domain import DomainParticipant
from cyclonedds.topic import Topic
from cyclonedds.pub import Publisher, DataWriter
from cyclonedds.util import duration, isgoodentity

from  testtopics import Message


def test_initialize_writer():
    dp = DomainParticipant(0)
    tp = Topic(dp, "Message", Message)
    pub = Publisher(dp)
    dw = DataWriter(pub, tp)

    assert isgoodentity(dw)


def test_writeto_writer():
    dp = DomainParticipant(0)
    tp = Topic(dp, "Message", Message)
    pub = Publisher(dp)
    dw = DataWriter(pub, tp)

    msg = Message(
        message="TestMessage"
    )

    dw.write(msg)
    assert dw.wait_for_acks(duration(seconds=1))