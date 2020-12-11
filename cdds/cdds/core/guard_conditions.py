import cdds
from cdds.core import Entity, DDSException
from cdds.internal import c_call, dds_entity_t, dds_return_t
from ctypes import POINTER, c_bool, byref


class GuardCondition(Entity):
    def __init__(self, domain_participant: 'cdds.domain.DomainParticipant'):
        super().__init__(self._create_guardcondition(domain_participant._ref))

    def set(self, triggered: bool) -> None:
        ret = self._set_guardcondition(self._ref, triggered)
        if ret < 0:
            raise DDSException(ret, f"Occurred when calling set on {repr(self)}")

    def read(self) -> bool:
        triggered = c_bool()
        ret = self._read_guardcondition(self._ref, byref(triggered))
        if ret < 0:
            raise DDSException(ret, f"Occurred when calling read on {repr(self)}")
        return bool(triggered)

    def take(self) -> bool:
        triggered = c_bool()
        ret = self._take_guardcondition(self._ref, byref(triggered))
        if ret < 0:
            raise DDSException(ret, f"Occurred when calling read on {repr(self)}")
        return bool(triggered)

    @c_call("dds_create_guardcondition")
    def _create_guardcondition(self, participant: dds_entity_t) -> dds_entity_t:
        pass

    @c_call("dds_set_guardcondition")
    def _set_guardcondition(self, guardcond: dds_entity_t, triggered: c_bool) -> dds_return_t:
        pass

    @c_call("dds_read_guardcondition")
    def _read_guardcondition(self, guardcond: dds_entity_t, triggered: POINTER(c_bool)) -> dds_return_t:
        pass

    @c_call("dds_take_guardcondition")
    def _take_guardcondition(self, guardcond: dds_entity_t, triggered: POINTER(c_bool)) -> dds_return_t:
        pass
