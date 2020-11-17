from cdds.core import Entity
from cdds.internal import c_call, dds_domainid_t, dds_qos_p_t, dds_listener_p_t, dds_entity_t


class DomainParticipant(Entity):
    def __init__(self, domain_id, qos=None, listener=None):
        self._ref = self._create_participant(domain_id, qos, listener)

    def __del__(self):
        self._delete_participant(self._ref)

    @c_call("dds_create_participant")
    def _create_participant(self, domain_id: dds_domainid_t, qos: dds_qos_p_t, listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @c_call("dds_delete")
    def _delete_participant(self, participant: dds_entity_t) -> None:
        pass
