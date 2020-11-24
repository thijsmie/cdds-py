from cdds.core import Entity
from cdds.internal import c_call, c_callable, DDSException, dds_entity_t, dds_return_t, dds_qos_p_t, dds_listener_p_t, dds_topic_descriptor_p_t

from ctypes import c_char, c_char_p, c_size_t, c_bool, c_void_p, byref, cast, POINTER
from typing import Optional


class Topic(Entity):
    def __init__(self, domain_participant: 'DomainParticipant', data_type, topic_name: str, qos=None, listener=None):
        self.data_type = data_type
        super().__init__(self._create_topic(domain_participant._ref, data_type.type_support, topic_name.encode(), qos._ref if qos else None, listener._ref if listener else None))

    def get_name(self, max_size=256):
        name = c_char * max_size
        ret = self._get_name(self._ref, byref(name[0]), max_size)
        if ret < 0:
            raise DDSException(ret, f"Occurred while fetching a topic name for {repr(self)}")
        return bytes(name).decode("ASCII")

    name = property(get_name, doc="Get topic name")

    def get_type_name(self, max_size=256):
        name = c_char * max_size
        ret = self._get_type_name(self._ref, byref(name[0]), max_size)
        if ret < 0:
            raise DDSException(ret, f"Occurred while fetching a topic type name for {repr(self)}")
        return bytes(name).decode("ASCII")

    typename = property(get_type_name, doc="Get topic type name")

    def set_filter(self, filter, arg=None):
        """Use proper filtering on readers instead."""
        raise NotImplementedError()

    def get_filter(self):
        """Use proper filtering on readers instead."""
        raise NotImplementedError()

    @c_call("dds_create_topic")
    def _create_topic(self, domain_participant: dds_entity_t, topic_descriptor: dds_topic_descriptor_p_t, topic_name: c_char_p, qos: dds_qos_p_t, listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @c_call("dds_get_name")
    def _get_name(self, topic: dds_entity_t, name: c_char_p, size: c_size_t) -> dds_return_t:
        pass

    @c_call("dds_get_type_name")
    def _get_type_name(self, topic: dds_entity_t, name: c_char_p, size: c_size_t) -> dds_return_t:
        pass


# TODO: dds_create_topic_generic
# TODO: dds_create_topic_arbitrary
