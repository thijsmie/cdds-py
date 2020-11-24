from cdds.core import Entity
from cdds.internal import c_call, dds_entity_t, dds_qos_p_t, dds_listener_p_t


class Subscriber(Entity):
    def __init__(self, domain_participant: 'DomainParticipant', qos=None, listener=None):
        super().__init__(self._create_subscriber(domain_participant._ref, qos._ref if qos else None, listener._ref if listener else None))

    @c_call("dds_create_subscriber")
    def _create_subscriber(self, domain_participant: dds_entity_t, qos: dds_qos_p_t, listener: dds_listener_p_t) -> dds_entity_t:
        pass

