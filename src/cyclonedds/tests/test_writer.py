import pytest

from cyclonedds.core import DDSException
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


def test_writer_instance_handle(common_setup):
    handle = common_setup.dw.register_instance(common_setup.msg)
    assert handle > 0
    common_setup.dw.write(common_setup.msg)
    common_setup.dw.unregister_instance(common_setup.msg)
