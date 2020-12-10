import pytest

from cdds.core import Entity
from cdds.domain import DomainParticipant
from cdds.topic import Topic
from cdds.sub import Subscriber, DataReader
from cdds.pub import Publisher, DataWriter
from cdds.core.exception import DDSException, DDS_RETCODE_PRECONDITION_NOT_MET
from cdds.util.entity import isgoodentity

from testtopics import Message


def test_create_participant():
    dp = DomainParticipant(0)
    assert isgoodentity(dp)


def test_find_topic():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, "Message")

    assert isgoodentity(tp)
    
    xtp = dp.find_topic("Message")

    assert xtp.typename == tp.typename
    assert xtp.name == tp.name

