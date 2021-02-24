import pytest

from cdds.core import Entity
from cdds.domain import DomainParticipant
from cdds.topic import Topic
from cdds.util.entity import isgoodentity

from  testtopics import Message


def test_create_topic():
    dp = DomainParticipant(0)
    tp = Topic(dp, "Message", Message)

    assert isgoodentity(tp)


def test_get_name():
    dp = DomainParticipant(0)
    tp = Topic(dp, 'MessageTopic', Message)

    assert tp.name == tp.get_name() == 'MessageTopic'

def test_get_type_name():
    dp = DomainParticipant(0)
    tp = Topic(dp, 'MessageTopic', Message)

    assert tp.typename == tp.get_type_name() == 'testtopics.message.Message'
