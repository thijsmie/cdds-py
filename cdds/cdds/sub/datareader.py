import cdds

from cdds.core import Entity, DDSException
from cdds.internal import c_call
from cdds.internal.dds_types import dds_entity_t, dds_qos_p_t, dds_listener_p_t, dds_return_t, dds_duration_t, SampleInfo
from cdds.core.exception import DDS_RETCODE_TIMEOUT

from ctypes import c_void_p, POINTER, c_size_t, c_uint32, cast, byref
from typing import Optional, Union


class SampleList(list):
    def __init__(self, entity, buf, bufsize, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity = entity
        self.buf = buf
        self.bufsize = bufsize

    def __del__(self):
        self.entity.return_loan(byref(cast(self.buf[0], c_void_p)), self.bufsize)



class DataReader(Entity):
    # TODO: support RHC (dds_create_reader_rhc)
    def __init__(self, subscriber_or_participant: Union['cdds.sub.Subscriber', 'cdds.domain.DomainParticipant'], topic: 'cdds.topic.Topic', qos=None, listener=None):
        self.topic = topic
        super().__init__(self._create_reader(subscriber_or_participant._ref, topic._ref, qos, listener._ref if listener else None))

    def read(self, N=1, condition=None):
        ref = condition._ref if condition else self._ref

        sample_info = (SampleInfo * N)()
        sample_info_pt = cast(sample_info, POINTER(SampleInfo))
        samples = (c_void_p * N)()

        ret = self._read(ref, samples, sample_info_pt, N, N)

        if ret < 0:
            raise DDSException(ret, f"Occurred when calling read() in {repr(self)}")

        if ret == 0:
            return []

        result_pt = cast(samples[0], POINTER(self.topic.data_type.struct_class))
        return_samples = [self.topic.data_type.from_struct(result_pt[i]) for i in range(min(ret, N))]
        retn = self._return_loan(ref, samples, min(N, ret))
        if retn < 0:
            raise DDSException(retn, f"Occured when returning loan for take(0 in {repr(self)}")
        return return_samples

    def take(self, N=1, condition=None):
        ref = condition._ref if condition else self._ref

        sample_info = (SampleInfo * N)()
        sample_info_pt = cast(sample_info, POINTER(SampleInfo))
        samples = (c_void_p * N)()

        ret = self._take(ref, samples, sample_info_pt, N, N)

        if ret < 0:
            raise DDSException(ret, f"Occurred when calling take() in {repr(self)}")

        if ret == 0:
            return []

        result_pt = cast(samples[0], POINTER(self.topic.data_type.struct_class))
        return_samples = [self.topic.data_type.from_struct(result_pt[i]) for i in range(min(ret, N))]
        retn = self._return_loan(ref, samples, min(N, ret))
        if retn < 0:
            raise DDSException(retn, f"Occured when returning loan for take(0 in {repr(self)}")
        return return_samples

    def wait_for_historical_data(self, timeout: int) -> bool:
        ret = self._wait_for_historical_data(self._ref, timeout)

        if ret == 0:
            return True
        elif ret == DDS_RETCODE_TIMEOUT:
            return False
        raise DDSException(ret, f"Occured while waiting for historical data in {repr(self)}")

    @c_call("dds_create_reader")
    def _create_reader(self, subscriber: dds_entity_t, topic: dds_entity_t, qos: dds_qos_p_t, listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @c_call("dds_return_loan")
    def _return_loan(self, reader: dds_entity_t, buff: POINTER(c_void_p), size: c_size_t) -> dds_return_t:
        pass

    @c_call("dds_read")
    def _read(self, reader: dds_entity_t, buffer: POINTER(c_void_p), sample_info: POINTER(SampleInfo), buffer_size: c_size_t, max_samples: c_uint32) -> dds_return_t:
        pass

    @c_call("dds_take")
    def _take(self, reader: dds_entity_t, buffer: POINTER(c_void_p), sample_info: POINTER(SampleInfo), buffer_size: c_size_t, max_samples: c_uint32) -> dds_return_t:
        pass

    @c_call("dds_reader_wait_for_historical_data")
    def _wait_for_historical_data(self, reader: dds_entity_t, max_wait: dds_duration_t) -> dds_return_t:
        pass
