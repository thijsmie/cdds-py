import pytest

from cdds.core import Entity
from cdds.core.exception import DDSException, DDS_RETCODE_UNSUPPORTED
from cdds.domain import DomainParticipant
from cdds.topic import Topic
from cdds.sub import Subscriber, DataReader
from cdds.util.time import duration


from testtopics import Message

def isgoodentity(v):
    return v != None and \
           isinstance(v, Entity) and \
           hasattr(v, "_ref") and \
           type(v._ref) == int and \
           v._ref > 0


def test_initialize_reader():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, "Message")
    sub = Subscriber(dp)
    dr = DataReader(sub, tp)

    assert isgoodentity(dr)
    
def test_initialize_reader_direct():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, "Message")
    dr = DataReader(dp, tp)

    assert isgoodentity(dr)


def test_readfrom_reader():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, "Message__DONOTPUBLISH")
    sub = Subscriber(dp)
    dr = DataReader(sub, tp)

    assert len(dr.read()) == 0


def test_takefrom_reader():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, "Message__DONOTPUBLISH")
    sub = Subscriber(dp)
    dr = DataReader(sub, tp)

    assert len(dr.take()) == 0


def test_waitforhistoricaldata_reader():
    dp = DomainParticipant(0)
    tp = Topic(dp, Message, "Message__DONOTPUBLISH")
    sub = Subscriber(dp)
    dr = DataReader(sub, tp)

    assert dr.wait_for_historical_data(duration(milliseconds=5))