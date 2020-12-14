import pytest

from cdds.core import Entity, Listener
from cdds.pub.datawriter import DataWriter
from cdds.sub import DataReader
from cdds.topic.topic import Topic
from cdds.util.entity import isgoodentity
from cdds.util.time import duration

from  testtopics import Message, MessageAlt


def test_listener_initialize():
    listener = Listener()


def test_listener_override():
    a = lambda reader: None
    listener = Listener(on_data_available=lambda reader: None)
    listener.set_on_data_available(lambda reader: None)


def test_listener_inheritance():
    class CListener(Listener):
        def on_data_available(self, reader: 'cdds.sub.DataReader') -> None:
            pass
    listener = CListener()


def test_listener_data_available(common_setup, capfd):
    listener = Listener(on_data_available=lambda reader: print("CHECK"))
    dr = DataReader(common_setup.sub, common_setup.tp, listener=listener)
    common_setup.dw.write(Message(message=b"Hi!"))

    out, err = capfd.readouterr()
    assert "CHECK" in out

