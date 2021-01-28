from ctypes import ArgumentError
from typing import Type
import pytest

from cdds.core import Entity
from cdds.core.exception import DDSException, DDS_RETCODE_BAD_PARAMETER
from cdds.domain import DomainParticipant
from cdds.topic import Topic
from cdds.sub import Subscriber, DataReader
from cdds.util import duration
from cdds.util.entity import isgoodentity


from  testtopics import Message

def test_reader_initialize():
    dp = DomainParticipant(0)
    tp = Topic(dp, "Message", Message)
    sub = Subscriber(dp)
    dr = DataReader(sub, tp)

    assert isgoodentity(dr)
    
def test_reader_initialize_direct():
    dp = DomainParticipant(0)
    tp = Topic(dp, "Message", Message)
    dr = DataReader(dp, tp)

    assert isgoodentity(dr)


def test_reader_read():
    dp = DomainParticipant(0)
    tp = Topic(dp, "Message__DONOTPUBLISH", Message)
    sub = Subscriber(dp)
    dr = DataReader(sub, tp)

    assert len(dr.read()) == 0


def test_reader_take():
    dp = DomainParticipant(0)
    tp = Topic(dp, "Message__DONOTPUBLISH", Message)
    sub = Subscriber(dp)
    dr = DataReader(sub, tp)

    assert len(dr.take()) == 0


def test_reader_waitforhistoricaldata():
    dp = DomainParticipant(0)
    tp = Topic(dp, "Message__DONOTPUBLISH", Message)
    sub = Subscriber(dp)
    dr = DataReader(sub, tp)

    assert dr.wait_for_historical_data(duration(milliseconds=5))


def test_reader_resizebuffer():
    dp = DomainParticipant(0)
    tp = Topic(dp, "Message__DONOTPUBLISH", Message)
    sub = Subscriber(dp)
    dr = DataReader(sub, tp)

    assert len(dr.read(N=100)) == 0
    assert len(dr.read(N=200)) == 0
    assert len(dr.read(N=100)) == 0


def test_reader_invalid():
    dp = DomainParticipant(0)
    tp = Topic(dp, "Message__DONOTPUBLISH", Message)
    sub = Subscriber(dp)
    dr = DataReader(sub, tp)

    with pytest.raises(TypeError):
        dr.read(-1)
    
    with pytest.raises(TypeError):
        dr.take(-1)
    