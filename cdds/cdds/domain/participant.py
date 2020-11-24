from ctypes import c_char_p
from cdds.core import Entity
from cdds.topic import Topic
from cdds.internal import c_call, DDSException
from cdds.internal.dds_types import dds_domainid_t, dds_qos_p_t, dds_listener_p_t, dds_entity_t
from cdds.internal.error import DDS_RETCODE_PRECONDITION_NOT_MET


class DomainParticipant(Entity):
    def __init__(self, domain_id=0, qos=None, listener=None):
        super().__init__(self._create_participant(domain_id, qos._ref if qos else None, listener._ref if listener else None))

    def find_topic(self, name):
        ret = self._find_topic(self._ref, name.encode("ASCII"))
        if ret > 0:
            # Note that this function returns a _new_ topic instance which we do not have in our entity list
            return Topic._init_from_retcode(ret)
        elif ret == DDS_RETCODE_PRECONDITION_NOT_MET:
            # Not finding a topic is not really an error from python standpoint
            return None

        raise DDSException(ret, f"Occurred when getting the participant of {repr(self)}")


    @c_call("dds_create_participant")
    def _create_participant(self, domain_id: dds_domainid_t, qos: dds_qos_p_t, listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @c_call("dds_find_topic")
    def _find_topic(self, participant: dds_entity_t, name: c_char_p) -> dds_entity_t:
        pass