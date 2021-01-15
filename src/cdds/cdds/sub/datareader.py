import cdds

from cdds.core import Entity, DDSException
from cdds.internal import c_call
from cdds.internal.dds_types import dds_entity_t, dds_qos_p_t, dds_listener_p_t, dds_return_t, dds_duration_t, SampleInfo
from cdds.core.exception import DDS_RETCODE_TIMEOUT

from ctypes import c_void_p, POINTER, c_size_t, c_uint32, cast, pointer
from typing import Union


class DataReader(Entity):
    """
    """

    def __init__(self, subscriber_or_participant: Union['cdds.sub.Subscriber', 'cdds.domain.DomainParticipant'],
                 topic: 'cdds.topic.Topic', qos=None, listener=None):
        self.topic = topic
        self._N = 0
        self._sampleinfos = None
        self._pt_sampleinfos = None
        self._samples = None
        self._pt_samples = None
        self._pt_void_samples = None
        super().__init__(
            self._create_reader(
                subscriber_or_participant._ref,
                topic._ref,
                qos._ref if qos else None,
                listener._ref if listener else None
            )
        )

    def _ensure_memory(self, N):
        if N <= self._N:
            return
        self._sampleinfos = (SampleInfo * N)()
        self._pt_sampleinfos = cast(self._sampleinfos, POINTER(SampleInfo))
        self._samples = (self.topic.data_type.struct_class * N)()
        self._pt_samples = (POINTER(self.topic.data_type.struct_class) * N)()
        for i in range(N):
            self._pt_samples[i] = pointer(self._samples[i])
        self._pt_void_samples = cast(self._pt_samples, POINTER(c_void_p))

    def read(self, N=1, condition=None):
        ref = condition._ref if condition else self._ref
        self._ensure_memory(N)

        ret = self._read(ref, self._pt_void_samples, self._pt_sampleinfos, N, N)

        if ret < 0:
            raise DDSException(ret, f"Occurred when calling read() in {repr(self)}")

        if ret == 0:
            return []

        return_samples = [self.topic.data_type.from_struct(self._samples[i]) for i in range(min(ret, N))]

        return return_samples

    def take(self, N=1, condition=None):
        ref = condition._ref if condition else self._ref
        self._ensure_memory(N)

        ret = self._take(ref, self._pt_void_samples, self._pt_sampleinfos, N, N)

        if ret < 0:
            raise DDSException(ret, f"Occurred when calling take() in {repr(self)}")

        if ret == 0:
            return []

        return_samples = [self.topic.data_type.from_struct(self._samples[i]) for i in range(min(ret, N))]

        return return_samples

    def wait_for_historical_data(self, timeout: int) -> bool:
        ret = self._wait_for_historical_data(self._ref, timeout)

        if ret == 0:
            return True
        elif ret == DDS_RETCODE_TIMEOUT:
            return False
        raise DDSException(ret, f"Occured while waiting for historical data in {repr(self)}")

    @c_call("dds_create_reader")
    def _create_reader(self, subscriber: dds_entity_t, topic: dds_entity_t, qos: dds_qos_p_t,
                       listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @c_call("dds_return_loan")
    def _return_loan(self, reader: dds_entity_t, buff: POINTER(c_void_p), size: c_size_t) -> dds_return_t:
        pass

    @c_call("dds_read")
    def _read(self, reader: dds_entity_t, buffer: POINTER(c_void_p), sample_info: POINTER(SampleInfo),
              buffer_size: c_size_t, max_samples: c_uint32) -> dds_return_t:
        pass

    @c_call("dds_take")
    def _take(self, reader: dds_entity_t, buffer: POINTER(c_void_p), sample_info: POINTER(SampleInfo),
              buffer_size: c_size_t, max_samples: c_uint32) -> dds_return_t:
        pass

    @c_call("dds_reader_wait_for_historical_data")
    def _wait_for_historical_data(self, reader: dds_entity_t, max_wait: dds_duration_t) -> dds_return_t:
        pass
