import pytest

from cdds.core import Entity
from cdds.domain import DomainParticipant
from cdds.topic import Topic

from testtopics import Message


def isgoodentity(v):
    return v != None and \
           isinstance(v, Entity) and \
           hasattr(v, "_ref") and \
           type(v._ref) == int and \
           v._ref > 0


def test_create_topic():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, 'Message')

    assert isgoodentity(tp)


def test_get_name():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, 'MessageTopic')

    assert tp.name == tp.get_name() == 'MessageTopic'

def test_get_type_name():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, 'MessageTopic')

    assert tp.typename == tp.get_type_name() == 'dds::Message'
