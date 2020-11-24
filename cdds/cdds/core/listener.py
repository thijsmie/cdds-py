from cdds.core import DDS, Entity
from cdds.internal import c_call, c_callable, dds_listener_p_t, dds_entity_t, dds_inconsistent_topic_status_t, dds_liveliness_lost_status_t, dds_liveliness_changed_status_t

from ctypes import c_void_p
from typing import Callable


dds_inconsistent_topic_fn = c_callable(None, [dds_entity_t, dds_inconsistent_topic_status_t, c_void_p])
dds_data_available_fn = c_callable(None, [dds_entity_t, c_void_p])
dds_liveliness_lost_fn = c_callable(None, [dds_entity_t, dds_liveliness_lost_status_t, c_void_p])
dds_liveliness_changed_fn = c_callable(None, [dds_entity_t, dds_liveliness_changed_status_t, c_void_p])


def is_override(func):
    obj = func.__self__
    prntM = getattr(super(type(obj), obj), func.__name__)

    return func.__func__ != prntM.__func__

class Listener(DDS):
    def __init__(self):
        super().__init__(self._create_listener(None))

        if is_override(self.on_data_available):
            self.set_on_data_available(self.on_data_available)

        if is_override(self.on_inconsistent_topic):
            self.set_on_inconsistent_topic(self.on_inconsistent_topic)
        
        if is_override(self.on_liveliness_lost):
            self.set_on_liveliness_lost(self.on_liveliness_lost)

        if is_override(self.on_liveliness_changed):
            self.set_on_liveliness_changed(self.on_liveliness_changed)
        
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

    def on_inconsistent_topic(self, reader: 'DataReader', status: dds_inconsistent_topic_status_t) -> None:
        pass

    def set_on_inconsistent_topic(self, callable: Callable[['DataReader'], None]):
        self.on_inconsistent_topic = callable
        if callable is None:
            self._set_inconsistent_topic(self._ref, None)
        else:
            def call(topic, status, arg):
                self.on_inconsistent_topic(Entity.get_entity(topic), status)
            self._on_inconsistent_topic = dds_inconsistent_topic_fn(call)
            self._set_inconsistent_topic(self._ref, self._on_inconsistent_topic)

    def on_data_available(self, reader: 'DataReader') -> None:
        pass

    def set_on_data_available(self, callable: Callable[['DataReader'], None]):
        self.on_data_available = callable
        if callable is None:
            self._set_data_available(self._ref, None)
        else:
            def call(reader, arg):
                self.on_data_available(Entity.get_entity(reader))
            self._on_data_available = dds_data_available_fn(call)
            self._set_data_available(self._ref, self._on_data_available)

    def on_liveliness_lost(self, writer: 'DataWriter', status: dds_liveliness_lost_status_t) -> None:
        pass

    def set_on_liveliness_lost(self, callable: Callable[['DataWriter', dds_liveliness_lost_status_t], None]):
        self.on_liveliness_lost = callable
        if callable is None:
            self._set_liveliness_lost(self._ref, None)
        else:
            def call(writer, status, arg):
                self.on_liveliness_lost(Entity.get_entity(writer), status)
            self._on_liveliness_lost = dds_liveliness_lost_fn(call)
            self._set_liveliness_lost(self._ref, self._on_liveliness_lost)

    def on_liveliness_changed(self, reader: 'DataReader', status: dds_liveliness_changed_status_t) -> None:
        pass

    def set_on_liveliness_changed(self, callable: Callable[['DataReader', dds_liveliness_changed_status_t], None]):
        self.on_liveliness_changed = callable
        if callable is None:
            self._set_liveliness_changed(self._ref, None)
        else:
            def call(reader, status, arg):
                self.on_liveliness_changed(Entity.get_entity(reader), status)
            self._on_liveliness_changed = dds_liveliness_changed_fn(call)
            self._set_liveliness_changed(self._ref, self._on_liveliness_changed)

    # TODO: on_offered_deadline_missed
    # TODO: on_offered_incompatible_qos
    # TODO: on_data_on_readers
    # TODO: on_sample_lost
    # TODO: on_sample_rejected
    # TODO: on_requested_deadline_missed
    # TODO: on_requested_incompatible_qos
    # TODO: on_publication_matched
    # TODO: on_subscription_matched

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

    @c_call("dds_lset_inconsistent_topic")
    def _set_inconsistent_topic(self, listener: dds_listener_p_t, callback: dds_inconsistent_topic_fn) -> None:
        pass

    @c_call("dds_lset_data_available")
    def _set_data_available(self, listener: dds_listener_p_t, callback: dds_data_available_fn) -> None:
        pass

    @c_call("dds_lset_liveliness_lost")
    def _set_liveliness_lost(self, listener: dds_listener_p_t, callback: dds_liveliness_lost_fn) -> None:
        pass

    @c_call("dds_lset_liveliness_changed")
    def _set_liveliness_changed(self, listener: dds_listener_p_t, callback: dds_liveliness_changed_fn) -> None:
        pass

    @c_call("dds_delete_listener")
    def _delete_listener(self, listener: dds_listener_p_t) -> None:
        pass

DDS.listener_type = Listener