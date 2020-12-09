from cdds.core import Entity, DDSException
from cdds.domain.participant import DomainParticipant
from cdds.internal import c_call, dds_entity_t, dds_return_t, dds_qos_p_t, dds_listener_p_t, dds_duration_t
from cdds.core.exception import DDS_RETCODE_TIMEOUT


class Publisher(Entity):
    def __init__(self, domain_participant: DomainParticipant, qos=None, listener=None):
        super().__init__(self._create_publisher(domain_participant._ref, qos._ref if qos else None, listener._ref if listener else None))

    def suspend(self):
        ret = self._suspend(self._ref)
        if ret == 0:
            return
        raise DDSException(ret, f"Occurred while suspending {repr(self)}")

    def resume(self):
        ret = self._resume(self._ref)
        if ret == 0:
            return
        raise DDSException(ret, f"Occurred while resuming {repr(self)}")

    def wait_for_acks(self, timeout: int):
        ret = self._wait_for_acks(self._ref, timeout)
        if ret == 0:
            return True
        elif ret == DDS_RETCODE_TIMEOUT:
            return False
        raise DDSException(ret, f"Occurred while waiting for acks from {repr(self)}")

    @c_call("dds_create_publisher")
    def _create_publisher(self, domain_participant: dds_entity_t, qos: dds_qos_p_t, listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @c_call("dds_suspend")
    def _suspend(self, publisher: dds_entity_t) -> dds_return_t:
        pass

    @c_call("dds_resume")
    def _resume(self, publisher: dds_entity_t) -> dds_return_t:
        pass

    @c_call("dds_wait_for_acks")
    def _wait_for_acks(self, publisher: dds_entity_t, timeout: dds_duration_t) -> dds_return_t:
        pass

