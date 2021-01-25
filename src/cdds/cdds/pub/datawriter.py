import cdds

from cdds.core import Entity, DDSException
from cdds.internal import c_call
from cdds.internal.dds_types import dds_entity_t, dds_duration_t, dds_qos_p_t, dds_listener_p_t, dds_return_t
from cdds.core.exception import DDS_RETCODE_TIMEOUT

from ctypes import c_void_p, byref

from ddspy import ddspy_write


class DataWriter(Entity):
    def __init__(self, publisher: 'cdds.pub.Publisher', topic: 'cdds.topic.Topic', qos=None, listener=None):
        super().__init__(
            self._create_writer(
                publisher._ref,
                topic._ref,
                qos._ref if qos else None,
                listener._ref if listener else None
            )
        )

    def write(self, sample):
        ret = ddspy_write(self._ref, sample)
        # ret = self._write(self._ref, sample.to_struct())
        if ret < 0:
            raise DDSException(ret, f"Occurred while writing sample in {repr(self)}")

    def wait_for_acks(self, timeout: int):
        ret = self._wait_for_acks(self._ref, timeout)
        if ret == 0:
            return True
        elif ret == DDS_RETCODE_TIMEOUT:
            return False
        raise DDSException(ret, f"Occurred while waiting for acks from {repr(self)}")

    def dispose(self, sample):
        if sample.struct:
            ret = self._dispose(self._ref, byref(sample.struct))
            if ret < 0:
                raise DDSException(ret, f"Occurred while disposing in {repr(self)}")

    # TODO: register_instance, unregister_instance
    # TODO: writedispose

    @c_call("dds_create_writer")
    def _create_writer(self, publisher: dds_entity_t, topic: dds_entity_t, qos: dds_qos_p_t,
                       listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @c_call("dds_write")
    def _write(self, writer: dds_entity_t, sample: c_void_p) -> dds_return_t:
        pass

    @c_call("dds_dispose")
    def _dispose(self, writer: dds_entity_t, sample: c_void_p) -> dds_return_t:
        pass

    @c_call("dds_wait_for_acks")
    def _wait_for_acks(self, publisher: dds_entity_t, timeout: dds_duration_t) -> dds_return_t:
        pass
