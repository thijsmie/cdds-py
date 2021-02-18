import cdds

from cdds.core import Entity, DDSException
from cdds.internal import c_call, dds_entity_t, dds_return_t, dds_qos_p_t, dds_listener_p_t, dds_topic_descriptor_p_t

from ctypes import c_char, c_char_p, c_size_t, cast
from ddspy import ddspy_topic_create


class Topic(Entity):
    """Representing a Topic"""

    def __init__(self, domain_participant: 'cdds.domain.DomainParticipant',
                 topic_name: str, data_type, qos=None, listener=None):
        self.data_type = data_type
        super().__init__(
            ddspy_topic_create(
                domain_participant._ref,
                topic_name,
                data_type,
                qos._ref if qos else None,
                listener._ref if listener else None
            )
        )

    def get_name(self, max_size=256):
        name = (c_char * max_size)()
        name_pt = cast(name, c_char_p)
        ret = self._get_name(self._ref, name_pt, max_size)
        if ret < 0:
            raise DDSException(ret, f"Occurred while fetching a topic name for {repr(self)}")
        return bytes(name).split(b'\0', 1)[0].decode("ASCII")

    name = property(get_name, doc="Get topic name")

    def get_type_name(self, max_size=256):
        name = (c_char * max_size)()
        name_pt = cast(name, c_char_p)
        ret = self._get_type_name(self._ref, name_pt, max_size)
        if ret < 0:
            raise DDSException(ret, f"Occurred while fetching a topic type name for {repr(self)}")
        return bytes(name).split(b'\0', 1)[0].decode("ASCII")

    typename = property(get_type_name, doc="Get topic type name")

    @c_call("dds_get_name")
    def _get_name(self, topic: dds_entity_t, name: c_char_p, size: c_size_t) -> dds_return_t:
        pass

    @c_call("dds_get_type_name")
    def _get_type_name(self, topic: dds_entity_t, name: c_char_p, size: c_size_t) -> dds_return_t:
        pass


# TODO: dds_create_topic_generic
# TODO: dds_create_topic_arbitrary
