from cdds.core import Entity
from cdds.domain.participant import DomainParticipant
from cdds.internal import c_call, dds_entity_t, dds_qos_p_t, dds_listener_p_t, dds_topic_descriptor_p_t
from ctypes import c_char_p

from typing import Optional


class Topic(Entity):
    topics = {}

    def __init__(self, domain_participant: DomainParticipant, data_type, topic_name: str, qos=None, listener=None):
        self.domain_participant = domain_participant
        self.data_type = data_type
        self.topic_name = topic_name
        self.qos = qos
        self.listener = listener

        self._ref = self._create_topic(domain_participant._ref, data_type.type_support(), topic_name.encode(), qos._ref if qos else None, listener._ref if listener else None)
        self.topics[self._ref] = self

    @c_call("dds_create_topic")
    def _create_topic(self, domain_participant: dds_entity_t, topic_descriptor: dds_topic_descriptor_p_t, topic_name: c_char_p, qos: dds_qos_p_t, listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @classmethod
    def get(cls, entity: dds_entity_t) -> Optional['Topic']:
        return cls.topics.get(entity, None)