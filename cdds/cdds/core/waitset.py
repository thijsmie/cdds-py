from cdds.core import Entity, DDSException
from cdds.internal import c_call
from cdds.internal.dds_types import dds_entity_t, dds_attach_t, dds_return_t, dds_duration_t, dds_time_t
from cdds.core.exception import DDS_RETCODE_TIMEOUT

from ctypes import c_size_t, c_int, c_void_p, c_bool, byref, cast, POINTER


class WaitSet(Entity):
    def __init__(self, domain_participant: 'cdds.domain.DomainParticipant'):
        super().__init__(self._create_waitset(domain_participant._ref))
        self.attached = []

    def __del__(self):
        for v in self.attached:
            self._waitset_detach(self._ref, v[0]._ref)
        super().__del__()

    def attach(self, entity: Entity) -> None:
        if self.is_attached(entity):
            return

        value_pt = c_int()

        ret = self._waitset_attach(self._ref, entity._ref, byref(value_pt))
        if ret < 0:
            raise DDSException(ret, f"Occurred when trying to attach {repr(entity)} to {repr(self)}")
        self.attached.append((entity, value_pt))

    def detach(self, entity: Entity) -> None:
        for i, v in enumerate(self.attached):
            if v[0] == entity:
                ret = self._waitset_detach(self._ref, entity._ref)
                if ret < 0:
                    raise DDSException(ret, f"Occurred when trying to attach {repr(entity)} to {repr(self)}")
                del self.attached[i]
                break

    def is_attached(self, entity: Entity) -> bool:
        for v in self.attached:
            if v[0] == entity:
                return True
        return False

    def get_entities(self):
        # Note: should spend some time on synchronisation. What if the waitset is used across threads? 
        # That is probably a bad idea in python, but who is going to stop the user from doing it anyway...
        return [v[0] for v in self.attached]

    def wait(self, timeout: int):
        cs = (c_void_p * len(self.attached))()
        pcs = cast(cs, c_void_p)
        ret = self._waitset_wait(self._ref, byref(pcs), len(self.attached), timeout)

        if ret >= 0:
            return ret
        
        raise DDSException(ret, f"Occurred while waiting in {repr(self)}")

    def wait_until(self, abstime: int):
        cs = (c_void_p * len(self.attached))()
        pcs = cast(cs, c_void_p)
        ret = self._waitset_wait_until(self._ref, byref(pcs), len(self.attached), abstime)

        if ret >= 0:
            return ret

        raise DDSException(ret, f"Occurred while waiting in {repr(self)}")

    def set_trigger(self, value: bool):
        ret = self._waitset_set_trigger(self._ref, value)
        if ret < 0:
            raise DDSException(ret, f"Occurred when setting trigger in {repr(self)}")


    @c_call("dds_create_waitset")
    def _create_waitset(self, domain_participant: dds_entity_t) -> dds_entity_t:
        pass

    @c_call("dds_waitset_attach")
    def _waitset_attach(self, waitset: dds_entity_t, entity: dds_entity_t, x: dds_attach_t) -> dds_return_t:
        pass

    @c_call("dds_waitset_detach")
    def _waitset_detach(self, waitset: dds_entity_t, entity: dds_entity_t) -> dds_return_t:
        pass

    @c_call("dds_waitset_wait")
    def _waitset_wait(self, waitset: dds_entity_t, xs: POINTER(dds_attach_t), nxs: c_size_t, reltimeout: dds_duration_t) -> dds_return_t:
        pass

    @c_call("dds_waitset_wait_until")
    def _waitset_wait_until(self, waitset: dds_entity_t, xs: POINTER(dds_attach_t), nxs: c_size_t, abstimeout: dds_duration_t) -> dds_return_t:
        pass

    @c_call("dds_waitset_set_trigger")
    def _waitset_set_trigger(self, waitset: dds_entity_t, value: c_bool) -> dds_return_t:
        pass
