import pytest

from cyclonedds.core import Listener
from cyclonedds.sub import DataReader

from testtopics import Message


def test_listener_initialize():
    listener = Listener()


def test_listener_override():
    a = lambda reader: None
    listener = Listener(on_data_available=lambda reader: None)
    listener.set_on_data_available(lambda reader: None)


def test_listener_inheritance():
    class CListener(Listener):
        def on_data_available(self, reader: 'cyclonedds.sub.DataReader') -> None:
            pass
    listener = CListener()


def test_listener_data_available(common_setup, capfd):
    listener = Listener(on_data_available=lambda reader: print("CHECK"))
    dr = DataReader(common_setup.sub, common_setup.tp, listener=listener)
    common_setup.dw.write(Message(message="Hi!"))

    out, err = capfd.readouterr()
    assert "CHECK" in out

