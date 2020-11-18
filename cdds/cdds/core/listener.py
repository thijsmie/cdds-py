from cdds.core import Entity
from cdds.topic import Topic
from cdds.sub import DataReader
from cdds.internal import c_call, c_callable, dds_listener_p_t, dds_entity_t, dds_inconsistent_topic_status_t

from ctypes import c_void_p
from typing import Callable


@c_callable
def dds_data_available_fn(reader: dds_entity_t, arg: c_void_p) -> None:
    pass


class Listener(Entity):
    def __init__(self):
        self._ref = self._create_listener(None)

        self._on_inconsistent_topic = None
        self._on_data_available = None
        self.__on_data_available = None

    def __del__(self):
        self._delete_listener(self._ref)

    def reset(self) -> None:
        self._reset_listener(self._ref)

    def copy(self) -> 'Listener':
        listener = Listener()
        self._copy_listener(listener._ref, self._ref)
        return listener

    def copy_to(self, listener: 'Listener') -> None:
        self._copy_listener(listener._ref, self._ref)

    def merge(self, listener: 'Listener') -> None:
        self._merge_listener(self._ref, listener._ref)

    #@c_callable
    #def _c_on_inconsistent_topic(self, topic: dds_entity_t, topic_status: dds_inconsistent_topic_status_t, arg: c_void_p) -> None:
    #    self._on_inconsistent_topic(Topic.get(topic), topic_status)

    #@property
    #def on_inconsistent_topic(self) -> Callable[[Topic], None]:
    #    return self._on_inconsistent_topic

    #@on_inconsistent_topic.setter
    #def on_inconsistent_topic(self, callable: Callable[[Topic, dds_inconsistent_topic_status_t], None]):
    #    if self._on_inconsistent_topic is None:
    #        if callable is None:
    #            return
    #        self._set_inconsistent_topic(self._ref, self._c_on_inconsistent_topic.bind(self))
    #    elif callable is None:
    #        self._set_inconsistent_topic(self._ref, None)
    #    self._on_inconsistent_topic = callable

    @property
    def on_data_available(self) -> Callable[[DataReader], None]:
        return self._on_data_available

    @on_data_available.setter
    def on_data_available(self, callable: Callable[[DataReader], None]):
        self._on_data_available = callable
        if callable is None:
            self._set_data_available(self._ref, None)
        else:
            def call(reader, arg):
                callable(DataReader.get(reader))
            self.__on_data_available = dds_data_available_fn(call)
            self._set_data_available(self._ref, self.__on_data_available)

    @c_call("dds_create_listener")
    def _create_listener(self, arg: c_void_p) -> dds_listener_p_t:
        pass

    @c_call("dds_reset_listener")
    def _reset_listener(self, listener: dds_listener_p_t) -> None:
        pass

    @c_call("dds_copy_listener")
    def _copy_listener(self, dst: dds_listener_p_t, src: dds_listener_p_t) -> None:
        pass

    @c_call("dds_merge_listener")
    def _merge_listener(self, dst: dds_listener_p_t, src: dds_listener_p_t) -> None:
        pass

    #@c_call("dds_lset_inconsistent_topic")
    #def _set_inconsistent_topic(self, listener: dds_listener_p_t, callback: _c_on_inconsistent_topic.type) -> None:
    #    pass

    @c_call("dds_lset_data_available")
    def _set_data_available(self, listener: dds_listener_p_t, callback: dds_data_available_fn) -> None:
        pass

    @c_call("dds_delete_listener")
    def _delete_listener(self, listener: dds_listener_p_t) -> None:
        pass

