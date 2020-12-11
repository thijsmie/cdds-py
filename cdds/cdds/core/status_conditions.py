import cdds

from cdds.internal import c_call, c_callable
from cdds.internal.dds_types import dds_entity_t, dds_return_t
from cdds.core import Entity, DDSException

from ctypes import c_uint32, c_void_p, c_bool, byref, cast, POINTER
from typing import Callable, Any


class SampleState:
    Read: int = 1
    NotRead: int = 2
    Any: int = 3


class ViewState:
    New: int = 4
    Old: int = 8
    Any: int = 12


class InstanceState:
    Alive: int = 16
    NotAliveDisposed: int = 32
    NotAliveNoWriters: int = 64
    Any: int = 112


class DDSStatus:
    InconsistentTopic = 1 << 1
    OfferedDeadlineMissed = 1 << 2
    RequestedDeadlineMissed = 1 << 3
    OfferedIncompatibleQos = 1 << 4
    RequestedIncompatibleQos = 1 << 5
    SampleLost = 1 << 6
    SampleRejected = 1 << 7
    DataOnReaders = 1 << 8
    DataAvailable = 1 << 9
    LivelinessLost = 1 << 10
    LivelinessChanged = 1 << 11
    PublicationMatched = 1 << 12
    SubscriptionMatched = 1 << 13
    All = (1 << 14) - 1


class Condition(Entity):
    """Utility class to implement common methods between Read and Queryconditions"""
    def get_mask(self) -> int:
        mask: c_uint32 = c_uint32()
        ret = self._get_mask(self._ref, byref(mask))
        if ret == 0:
            return mask.value
        raise DDSException(ret, f"Occurred when obtaining the mask of {repr(self)}")

    def is_triggered(self) -> bool:
        ret = self._triggered(self._ref)
        if ret < 0:
            raise DDSException(ret, f"Occurred when checking if {repr(self)} was triggered")
        return ret == 1

    triggered: bool = property(is_triggered)

    @c_call("dds_get_mask")
    def _get_mask(self, condition: dds_entity_t, mask: POINTER(c_uint32)) -> dds_return_t:
        pass

    @c_call("dds_triggered")
    def _triggered(self, condition: dds_entity_t) -> dds_return_t:
        pass


class ReadCondition(Condition):
    def __init__(self, reader: 'cdds.sub.DataReader', mask: int) -> None:
        self.reader = reader
        self.mask = mask
        super().__init__(self._create_readcondition(reader._ref, mask))

    @c_call("dds_create_readcondition")
    def _create_readcondition(self, reader: dds_entity_t, mask: c_uint32) -> dds_entity_t:
        pass


querycondition_filter_fn = c_callable(c_bool, [c_void_p])


class QueryCondition(Condition):
    def __init__(self, reader: 'cdds.sub.DataReader', mask: int, filter: Callable[[Any], bool]) -> None:
        self.reader = reader
        self.mask = mask
        self.filter = filter

        def call(sample_pt):
            try:
                return self.filter(cast(sample_pt, POINTER(reader.topic.data_type))[0])
            except Exception:  # Block any python exception from going into C
                return False

        self._filter = querycondition_filter_fn(call)
        super().__init__(self._create_querycondition(reader._ref, mask, self._filter))

    @c_call("dds_create_querycondition")
    def _create_querycondition(self, reader: dds_entity_t, mask: c_uint32, filter: querycondition_filter_fn) -> dds_entity_t:
        pass
