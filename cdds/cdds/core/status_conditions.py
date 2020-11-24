from cdds.internal import c_call, c_callable, DDSException
from cdds.internal.dds_types import dds_entity_t, dds_attach_t, dds_return_t, dds_duration_t, dds_time_t
from cdds.core import Entity

from ctypes import c_uint32, c_size_t, c_int, c_void_p, c_bool, byref, cast, POINTER
from typing import Callable, Any


class SampleState:
    Read = 1
    NotRead = 2
    Any = 3


class ViewState:
    New = 4
    Old = 8
    Any = 12


class InstanceState:
    Alive = 16
    NotAliveDisposed = 32
    NotAliveNoWriters = 64
    Any = 112


class Condition(Entity):
    """Utility class to implement common methods between Read and Queryconditions"""
    def get_mask(self):
        mask = c_uint32()
        ret = self._get_mask(self._ref, byref(mask))
        if ret == 0:
            return int(mask)
        raise DDSException(ret, f"Occurred when obtaining the mask of {repr(self)}.")

    @c_call("dds_get_mask")
    def _get_mask(self, condition: dds_entity_t, mask: POINTER(c_uint32)):
        pass

class ReadCondition(Condition):
    def __init__(self, reader: 'DataReader', mask: int) -> None:
        self.reader = reader
        self.mask = mask
        super().__init__(self._create_readcondition(reader._ref, mask))

    @c_call("dds_create_readcondition")
    def _create_readcondition(self, reader: dds_entity_t, mask: c_uint32) -> dds_entity_t:
        pass


dds_querycondition_filter_fn = c_callable(c_bool, [c_void_p])
class QueryCondition(Condition):
    def __init__(self, reader: 'DataReader', mask: int, filter: Callable[[Any], bool]) -> None:
        self.reader = reader
        self.mask = mask
        self.filter = filter
        
        def call(sample_pt):
            try:
                return self.filter(cast(sample_pt, POINTER(reader.topic.data_type))[0])
            except:
                return False

        self._filter = dds_querycondition_filter_fn(call)
        super().__init__(self._create_querycondition(reader._ref, mask, self._filter))

    @c_call("dds_create_querycondition")
    def _create_querycondition(self, reader: dds_entity_t, mask: c_uint32, filter: dds_querycondition_filter_fn) -> dds_entity_t:
        pass