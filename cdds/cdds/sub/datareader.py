from cdds.core import Entity
from cdds.sub import Subscriber
from cdds.topic import Topic
from cdds.internal import c_call, dds_entity_t, dds_qos_p_t, dds_listener_p_t, dds_return_t, SampleInfo
from ctypes import c_void_p, c_int, POINTER, c_size_t, c_uint32, cast

from typing import Optional


class DataReader(Entity):
    readers = {}

    def __init__(self, subscriber: Subscriber, topic: Topic, qos=None, listener=None):
        self.subscriber = subscriber
        self.topic = topic
        self.qos = qos
        self.listener = listener
        self._ref = self._create_reader(subscriber._ref, topic._ref, qos, listener._ref if listener else None)
        self.readers[self._ref] = self

    @classmethod
    def get(self, entity: dds_entity_t) -> Optional['DataReader']:
        return self.readers.get(entity, None)

    def read(self, N=1):
        # TODO: Alloc these statically
        sample_info = (SampleInfo * N)()
        sample_info_pt = cast(sample_info, POINTER(SampleInfo))
        samples = (c_void_p * N)()

        retcode = self._read(self._ref, samples, sample_info_pt, N, N)

        if retcode <= 0:
            return None

        return [cast(samples[i], POINTER(self.topic.data_type))[i] for i in range(N)]

    def take(self, N=1):
        # TODO: Alloc these statically
        sample_info = (SampleInfo * N)()
        sample_info_pt = cast(sample_info, POINTER(SampleInfo))
        samples = (c_void_p * N)()

        retcode = self._take(self._ref, samples, sample_info_pt, N, N)

        if retcode <= 0:
            return None

        return [cast(samples[i], POINTER(self.topic.data_type))[i] for i in range(N)]

    def dispose(self, sample):
        return self._dispose(self._ref, sample._ref)

    @c_call("dds_create_reader")
    def _create_reader(self, subscriber: dds_entity_t, topic: dds_entity_t, qos: dds_qos_p_t, listener: dds_listener_p_t) -> dds_entity_t:
        pass

    @c_call("dds_dispose")
    def _dispose(self, reader: dds_entity_t, sample: c_void_p) -> dds_return_t:
        pass

    @c_call("dds_read")
    def _read(self, reader: dds_entity_t, buffer: POINTER(c_void_p), sample_info: POINTER(SampleInfo), buffer_size: c_size_t, max_samples: c_uint32) -> dds_return_t:
        pass

    @c_call("dds_take")
    def _take(self, reader: dds_entity_t, buffer: POINTER(c_void_p), sample_info: POINTER(SampleInfo), buffer_size: c_size_t, max_samples: c_uint32) -> dds_return_t:
        pass
