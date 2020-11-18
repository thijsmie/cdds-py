from cdds.internal import c_call
from cdds.internal.dds_types import dds_entity_t, dds_attach_t, dds_return_t
from cdds.core import Entity
from cdds.domain import DomainParticipant

from ctypes import c_int


class WaitSet(Entity):
    def __init__(self, domain_participant: DomainParticipant):
        self._ref = self._create_waitset(domain_participant._ref)
        self.attached = []

    def __del__(self):
        self._destroy_waitset(self._ref)

    def attach(self, entity: Entity):
        if self.is_attached(entity):
            return

        value_pt = c_int()
        self._waitset_attach(self._ref, entity._ref, byref(value_pt))
        self.attached.append((entity, value_pt))

    def detach(self, entity: Entity):
        for i, v in enumerate(self.attached):
            if v[0] == entity:
                self._waitset_detach(self._ref, entity._ref)
                del self.attached[i]
                break

    def is_attached(self, entity: Entity):
        for v in self.attached:
            if v[0] == entity:
                return True
        return False

    def wait(self, n_blobs, timeout):
        # we only have one condition
        cs = (c_void_p * 1)()
        pcs = cast(cs, c_void_p)
        s = self.rt.ddslib.dds_waitset_wait(self.handle, byref(pcs), 1, timeout)
        if s == 0:
            return False
        else:
            return True

    @c_call("dds_create_waitset")
    def _create_waitset(self, domain_participant: dds_entity_t) -> dds_entity_t:
        pass

    @c_call("dds_waitset_attach")
    def _waitset_attach(self, waitset: dds_entity_t, entity: dds_entity_t, x: dds_attach_t) -> dds_return_t:
        pass

    @c_call("dds_delete")
    def _destroy_waitset(self, waitset: dds_entity_t) -> None:
        passs