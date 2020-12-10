from cdds.internal import DDS, c_call
from cdds.internal.dds_types import dds_qos_p_t, dds_return_t, dds_reliability_t, dds_durability_t, dds_duration_t, dds_history_t, \
    dds_presentation_access_scope_t, dds_ownership_t, dds_liveliness_t, dds_destination_order_t, dds_ingnorelocal_t
from cdds.util.time import duration

from ctypes import c_void_p, c_int32, c_char_p, POINTER, c_size_t, c_uint32, c_bool, cast, byref, pointer, sizeof, Structure
from enum import Enum, auto
from typing import Tuple, Callable, Optional, List, Any



class _QosReliability(Enum):
    BestEffort = 0
    Reliable = 1


class _QosDurability(Enum):
    Volatile = 0
    TransientLocal = 1
    Transient = 2
    Persistent = 3


class _QosHistory(Enum):
    KeepLast = 0
    KeepAll = 1


class _QosAccessScope(Enum):
    Instance = 0
    Topic = 1
    Group = 2


class _QosOwnership(Enum):
    Shared = 0
    Exclusive = 1


class _QosLiveliness(Enum):
    Automatic = 0
    ManualByParticipant = 1
    ManualByTopic = 2


class _QosDestinationOrder(Enum):
    ByReceptionTimestamp = 0
    BySourceTimestamp = 1


class _QosIgnoreLocal(Enum):
    Nothing = 0
    Participant = 1
    Process = 2


class _PolicyType(Enum):
    Reliability = auto()
    Durability = auto()
    History = auto()
    ResourceLimits = auto()
    PresentationAccessScope = auto()
    Lifespan = auto()
    Deadline = auto()
    LatencyBudget = auto()
    Ownership = auto()
    OwnershipStrength = auto()
    Liveliness = auto()
    TimeBasedFilter = auto()
    Partitions = auto()
    TransportPriority = auto()
    DestinationOrder = auto()
    WriterDataLifecycle = auto()
    ReaderDataLifecycle = auto()
    DurabilityService = auto()
    IgnoreLocal = auto()


class Policy:
    class Reliability:
        @staticmethod
        def BestEffort(max_blocking_time: int) -> Tuple[_PolicyType, Tuple[_QosReliability, int]]:
            return _PolicyType.Reliability, (_QosReliability.BestEffort, max_blocking_time)
            
        @staticmethod
        def Reliable(max_blocking_time: int) -> Tuple[_PolicyType, Tuple[_QosReliability, int]]:
            return _PolicyType.Reliability, (_QosReliability.Reliable, max_blocking_time)

    class Durability:
        Volatile: Tuple[_PolicyType, _QosDurability] = (_PolicyType.Durability, _QosDurability.Volatile)
        TransientLocal: Tuple[_PolicyType, _QosDurability] = (_PolicyType.Durability, _QosDurability.TransientLocal)
        Transient: Tuple[_PolicyType, _QosDurability] = (_PolicyType.Durability, _QosDurability.Transient)
        Persistent: Tuple[_PolicyType, _QosDurability] = (_PolicyType.Durability, _QosDurability.Persistent)
    
    class History:
        KeepAll: Tuple[_PolicyType, Tuple[_QosHistory, int]] = (_PolicyType.History, (_QosHistory.KeepAll, 0))
        @staticmethod
        def KeepLast(amount: int) -> Tuple[_PolicyType, Tuple[_QosHistory, int]]:
            return _PolicyType.History, (_QosHistory.KeepLast, amount)

    @staticmethod
    def ResourceLimits(max_samples: int, max_instances: int, max_samples_per_instance: int) -> Tuple[_PolicyType, Tuple[int, int, int]]:
        return _PolicyType.ResourceLimits, (max_samples, max_instances, max_samples_per_instance)

    class PresentationAccessScope:
        @staticmethod
        def Instance(coherent_access: bool, ordered_access: bool) -> Tuple[_PolicyType, Tuple[_QosAccessScope, bool, bool]]:
            return _PolicyType.PresentationAccessScope, (_QosAccessScope.Instance, coherent_access, ordered_access)

        @staticmethod
        def Topic(coherent_access: bool, ordered_access: bool) -> Tuple[_PolicyType, Tuple[_QosAccessScope, bool, bool]]:
            return _PolicyType.PresentationAccessScope, (_QosAccessScope.Topic, coherent_access, ordered_access)

        @staticmethod
        def Group(coherent_access: bool, ordered_access: bool) -> Tuple[_PolicyType, Tuple[_QosAccessScope, bool, bool]]:
            return _PolicyType.PresentationAccessScope, (_QosAccessScope.Group, coherent_access, ordered_access)

    @staticmethod
    def Lifespan(lifespan: int) -> Tuple[_PolicyType, int]:
        return _PolicyType.Lifespan, lifespan

    @staticmethod
    def Deadline(deadline: int) -> Tuple[_PolicyType, int]:
        return _PolicyType.Deadline, deadline

    @staticmethod
    def LatencyBudget(budget: int) -> Tuple[_PolicyType, int]:
        return _PolicyType.LatencyBudget, budget
    class Ownership:
        Shared: Tuple[_PolicyType, _QosOwnership] = (_PolicyType.Ownership, _QosOwnership.Shared)
        Exclusive: Tuple[_PolicyType, _QosOwnership] = (_PolicyType.Ownership, _QosOwnership.Exclusive)

    @staticmethod
    def OwnershipStrength(strength: int) -> Tuple[_PolicyType, int]:
        return _PolicyType.OwnershipStrength, strength

    class Liveliness:
        @staticmethod
        def Automatic(lease_duration: int) -> Tuple[_PolicyType, Tuple[_QosLiveliness, int]]:
            return _PolicyType.Liveliness, (_QosLiveliness.Automatic, lease_duration)

        @staticmethod
        def ManualByParticipant(lease_duration: int) -> Tuple[_PolicyType, Tuple[_QosLiveliness, int]]:
            return _PolicyType.Liveliness, (_QosLiveliness.ManualByParticipant, lease_duration)

        @staticmethod
        def ManualByTopic(lease_duration: int) -> Tuple[_PolicyType, Tuple[_QosLiveliness, int]]:
            return _PolicyType.Liveliness, (_QosLiveliness.ManualByTopic, lease_duration)

    @staticmethod
    def TimeBasedFilter(filter: int) -> Tuple[_PolicyType, int]:
        return _PolicyType.TimeBasedFilter, filter
    
    @staticmethod
    def Partitions(*partitions: List[str]) -> Tuple[_PolicyType, List[str]]:
        return _PolicyType.Partitions, partitions

    @staticmethod
    def TransportPriority(priority: int) -> Tuple[_PolicyType, int]:
        return _PolicyType.TransportPriority, priority

    class DestinationOrder:
        ByReceptionTimestamp: Tuple[_PolicyType, _QosDestinationOrder] = (_PolicyType.DestinationOrder, _QosDestinationOrder.ByReceptionTimestamp)
        BySourceTimestamp: Tuple[_PolicyType, _QosDestinationOrder] = (_PolicyType.DestinationOrder, _QosDestinationOrder.BySourceTimestamp)

    @staticmethod
    def WriterDataLifecycle(autodispose: bool) -> Tuple[_PolicyType, bool]:
        return _PolicyType.WriterDataLifecycle, autodispose

    @staticmethod
    def ReaderDataLifecycle(autopurge_nowriter_samples_delay: int, autopurge_disposed_samples_delay: int) -> Tuple[_PolicyType, Tuple[int, int]]:
        return _PolicyType.ReaderDataLifecycle, (autopurge_nowriter_samples_delay, autopurge_disposed_samples_delay)

    @staticmethod
    def DurabilityService(cleanup_delay: int, history: Tuple[_PolicyType, Tuple[_QosHistory, int]], max_samples: int, max_instances: int, \
         max_samples_per_instance) -> Tuple[_PolicyType, Tuple[int, _QosHistory, int, int, int, int]]:
         assert (history[0] == _PolicyType.History)
         return _PolicyType.DurabilityService, (cleanup_delay, history[1][0], history[1][1], max_samples, max_instances, max_samples_per_instance)

    class IgnoreLocal:
        Nothing: Tuple[_PolicyType, _QosDestinationOrder] = (_PolicyType.IgnoreLocal, _QosIgnoreLocal.Nothing)
        Participant: Tuple[_PolicyType, _QosDestinationOrder] = (_PolicyType.IgnoreLocal, _QosIgnoreLocal.Participant)
        Process: Tuple[_PolicyType, _QosIgnoreLocal] = (_PolicyType.IgnoreLocal, _QosIgnoreLocal.Process)

class QosException(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"[Qos] {self.msg}"

    __repr__ = __str__


class Qos(DDS):
    _qosses = {}
    _attr_dispatch = {
        _PolicyType.Reliability: "set_reliability",
        _PolicyType.Durability: "set_durability",
        _PolicyType.History: "set_history",
        _PolicyType.ResourceLimits: "set_resource_limits",
        _PolicyType.PresentationAccessScope: "set_presentation_access_scope",
        _PolicyType.Lifespan: "set_lifespan",
        _PolicyType.Deadline: "set_deadline",
        _PolicyType.LatencyBudget: "set_latency_budget",
        _PolicyType.Ownership: "set_ownership",
        _PolicyType.OwnershipStrength: "set_ownership_strength",
        _PolicyType.Liveliness: "set_liveliness",
        _PolicyType.TimeBasedFilter: "set_time_based_filter",
        _PolicyType.Partitions: "set_partitions",
        _PolicyType.TransportPriority: "set_transport_priority",
        _PolicyType.DestinationOrder: "set_destination_order",
        _PolicyType.WriterDataLifecycle: "set_writer_data_lifecycle",
        _PolicyType.ReaderDataLifecycle: "set_reader_data_lifecycle",
        _PolicyType.DurabilityService: "set_durability_service",
        _PolicyType.IgnoreLocal: "set_ignore_local"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(self._create_qos())
        self._qosses[self._ref] = self

        self._pre_alloc_data_pointers()

        for policy in args:
            if not policy or len(policy) < 2 or policy[0] not in self._attr_dispatch:
                raise QosException(f"Passed invalid argument to Qos: {policy}")
            getattr(self, self._attr_dispatch[policy[0]])(policy)

        for name, value in kwargs.items():
            if name == "userdata":
                self.set_userdata(value)
            elif name == "topicdata":
                self.set_topicdata(value)
            elif name == "groupdata":
                self.set_groupdata(value)
            elif name == "props":
                for prop_name, prop_value in value.items():
                    self.set_prop(prop_name, prop_value)
            elif name == "bprops":
                for prop_name, prop_value in value.items():
                    self.set_bprop(prop_name, prop_value)
            else:
                setattr(self, name, value)

    def __iadd__(self, policy):
        if not policy or len(policy) < 2 or policy[0] not in self._attr_dispatch:
            raise QosException(f"Passed invalid argument to Qos: {policy}")
        getattr(self, self._attr_dispatch[policy[0]])(policy)
        return self

    @classmethod
    def get_qos(cls, id):
        return cls._qosses.get(id)

    def __del__(self):
        self._delete_qos(self._ref)

    def __eq__(self, o: 'Qos') -> bool:
        return self._eq(self._ref, o._ref)

    def get_userdata(self) -> Tuple[c_size_t, c_void_p]:
        if not self._get_userdata(self._ref, byref(self._gc_userdata_value), byref(self._gc_userdata_size)):
            raise QosException("Userdata or Qos object invalid.")

        if self._gc_userdata_size == 0:
            return None, 0

        return self._gc_userdata_value, self._gc_userdata_value

    def get_userdata_as(self, _type: type) -> Any:
        if not self._get_userdata(self._ref, byref(self._gc_userdata_value), byref(self._gc_userdata_size)):
            raise QosException("Userdata or Qos object invalid.")

        if self._gc_userdata_size == 0:
            return None

        if sizeof(_type) != self._gc_userdata_value:
            raise QosException("Could not decode userdata to struct.")

        struct = cast(self._gc_userdata_value, POINTER(_type))

        return struct[0]

    def get_topicdata(self) -> Tuple[c_size_t, c_void_p]:
        if not self._get_topicdata(self._ref, byref(self._gc_topicdata_value), byref(self._gc_topicdata_size)):
            raise QosException("topicdata or Qos object invalid.")

        if self._gc_topicdata_size == 0:
            return None, 0

        return self._gc_topicdata_value, self._gc_topicdata_value

    def get_topicdata_as(self, _type: type) -> Any:
        if not self._get_topicdata(self._ref, byref(self._gc_topicdata_value), byref(self._gc_topicdata_size)):
            raise QosException("topicdata or Qos object invalid.")

        if self._gc_topicdata_size == 0:
            return None

        if sizeof(_type) != self._gc_topicdata_value:
            raise QosException("Could not decode topicdata to struct.")

        struct = cast(self._gc_topicdata_value, POINTER(_type))

        return struct[0]

    def get_groupdata(self) -> Tuple[c_size_t, c_void_p]:
        if not self._get_groupdata(self._ref, byref(self._gc_groupdata_value), byref(self._gc_groupdata_size)):
            raise QosException("groupdata or Qos object invalid.")

        if self._gc_groupdata_size == 0:
            return None, 0

        return self._gc_groupdata_value, self._gc_groupdata_value

    def get_groupdata_as(self, _type: type) -> Any:
        if not self._get_groupdata(self._ref, byref(self._gc_groupdata_value), byref(self._gc_groupdata_size)):
            raise QosException("groupdata or Qos object invalid.")

        if self._gc_groupdata_size == 0:
            return None

        if sizeof(_type) != self._gc_groupdata_value:
            raise QosException("Could not decode groupdata to struct.")

        struct = cast(self._gc_groupdata_value, POINTER(_type))

        return struct[0]

    def get_durability(self) -> Tuple[_PolicyType, _QosDurability]:
        if not self._get_durability(self._ref, byref(self._gc_durability)):
            raise QosException("Durability or Qos object invalid.")

        return _PolicyType.Durability, _QosDurability(self._gc_durability.value)

    def get_history(self) -> Tuple[_PolicyType, Tuple[_QosHistory, int]]:
        if not self._get_history(self._ref, byref(self._gc_history), byref(self._gc_history_depth)):
            raise QosException("History or Qos object invalid.")

        return _PolicyType.History, (_QosHistory(self._gc_history.value), self._gc_history_depth.value)

    def get_resource_limits(self) -> Tuple[_PolicyType, Tuple[int, int, int]]:
        if not self._get_resource_limits(self._ref, byref(self._gc_max_samples), byref(self._gc_max_instances), byref(self._gc_max_samples_per_instance)):
            raise QosException("Resource limits or Qos object invalid.")

        return _PolicyType.ResourceLimits, (self._gc_max_samples.value, self._gc_max_instances.value, self._gc_max_samples_per_instance.value)

    def get_presentation_access_scope(self) -> Tuple[_PolicyType, Tuple[_QosAccessScope, bool, bool]]:
        if not self._get_presentation(self._ref, byref(self._gc_access_scope), byref(self._gc_coherent_access), byref(self._gc_ordered_access)):
            raise QosException("Presentation or Qos object invalid.")
        
        return _PolicyType.PresentationAccessScope, (_QosAccessScope(self._gc_access_scope.value), bool(self._gc_coherent_access), bool(self._gc_ordered_access))

    def get_lifespan(self) -> Tuple[_PolicyType, int]:
        if not self._get_lifespan(self._ref, byref(self._gc_lifespan)):
            raise QosException("Lifespan or Qos object invalid.")

        return _PolicyType.Lifespan, self._gc_lifespan.value

    def get_deadline(self) -> Tuple[_PolicyType, int]:
        if not self._get_deadline(self._ref, byref(self._gc_deadline)):
            raise QosException("Deadline or Qos object invalid.")

        return _PolicyType.Deadline, self._gc_deadline.value

    def get_latency_budget(self) -> Tuple[_PolicyType, int]:
        if not self._get_latency_budget(self._ref, byref(self._gc_latency_budget)):
            raise QosException("Deadline or Qos object invalid.")

        return _PolicyType.LatencyBudget, self._gc_latency_budget.value

    def get_ownership(self) -> Tuple[_PolicyType, _QosOwnership]:
        if not self._get_ownership(self._ref, byref(self._gc_ownership)):
            raise QosException("Ownership or Qos object invalid.")

        return _PolicyType.Ownership, _QosOwnership(self._gc_ownership.value)

    def get_ownership_strength(self) -> Tuple[_PolicyType, int]:
        if not self._get_ownership_strength(self._ref, byref(self._gc_ownership_strength)):
            raise QosException("Ownership strength or Qos object invalid.")

        return _PolicyType.OwnershipStrength, self._gc_ownership_strength.value

    def get_liveliness(self) -> Tuple[_PolicyType, Tuple[_QosLiveliness, int]]:
        if not self._get_liveliness(self._ref, byref(self._gc_liveliness), byref(self._gc_lease_duration)):
            raise QosException("Liveliness or Qos object invalid.")

        return _PolicyType.Liveliness, (_QosLiveliness(self._gc_liveliness.value), self._gc_lease_duration.value)

    def get_time_based_filter(self) -> Tuple[_PolicyType, int]:
        if not self._get_time_based_filter(self._ref, byref(self._gc_time_based_filter)):
            raise QosException("Time Based Filter or Qos object invalid.")

        return _PolicyType.TimeBasedFilter, self._gc_time_based_filter.value

    def get_partitions(self) -> Tuple[_PolicyType, List[str]]:
        if not self._get_partitions(self._ref, byref(self._gc_partition_num), byref(self._gc_partition_names)):
            raise QosException("Partition or Qos object invalid.")

        names = [None] * self._gc_partition_num.value
        for i in range(self._gc_partition_num.value):
            names[i] = bytes(self._gc_partition_names[i]).decode()

        return _PolicyType.Partitions, tuple(names)

    def get_reliability(self) -> Tuple[_PolicyType, Tuple[_QosReliability, int]]:
        if not self._get_reliability(self._ref, byref(self._gc_reliability), byref(self._gc_max_blocking_time)):
            raise QosException("Reliability or Qos object invalid.")

        return _PolicyType.Reliability, (_QosReliability(self._gc_reliability.value), self._gc_max_blocking_time.value)

    def get_transport_priority(self) -> Tuple[_PolicyType, int]:
        if not self._get_transport_priority(self._ref, byref(self._gc_transport_priority)):
            raise QosException("Transport Priority or Qos object invalid.")

        return _PolicyType.TransportPriority, self._gc_transport_priority.value

    def get_destination_order(self) -> Tuple[_PolicyType, _QosDestinationOrder]:
        if not self._get_destination_order(self._ref, byref(self._gc_destination_order)):
            raise QosException("Destination Order or Qos object invalid.")

        return _PolicyType.DestinationOrder, _QosDestinationOrder(self._gc_destination_order.value)

    def get_writer_data_lifecycle(self) -> Tuple[_PolicyType, bool]:
        if not self._get_writer_data_lifecycle(self._ref, byref(self._gc_writer_autodispose)):
            raise QosException("Writer Data Lifecycle or Qos object invalid.")

        return _PolicyType.WriterDataLifecycle, bool(self._gc_writer_autodispose)

    def get_reader_data_lifecycle(self) -> Tuple[_PolicyType, Tuple[int, int]]:
        if not self._get_reader_data_lifecycle(self._ref, byref(self._gc_autopurge_nowriter_samples_delay), byref(self._gc_autopurge_disposed_samples_delay)):
            raise QosException("Reader Data Lifecycle or Qos object invalid.")

        return _PolicyType.ReaderDataLifecycle, (self._gc_autopurge_nowriter_samples_delay.value, self._gc_autopurge_disposed_samples_delay.value)

    def get_durability_service(self) -> Tuple[_PolicyType, Tuple[int, _QosHistory, int, int, int, int]]:
        if not self._get_durability_service(self._ref, 
            byref(self._gc_durservice_service_cleanup_delay), 
            byref(self._gc_durservice_history_kind), 
            byref(self._gc_durservice_history_depth), 
            byref(self._gc_durservice_max_samples), 
            byref(self._gc_durservice_max_instances), 
            byref(self._gc_durservice_max_samples_per_instance)):
            raise QosException("Durability Service or Qos object invalid.")

        return _PolicyType.DurabilityService, (self._gc_durservice_service_cleanup_delay.value, \
             _QosHistory(self._gc_durservice_history_kind.value), self._gc_durservice_history_depth.value,
             self._gc_durservice_max_samples.value, self._gc_durservice_max_instances.value, \
             self._gc_durservice_max_samples_per_instance.value)

    def get_ignore_local(self) -> Tuple[_PolicyType, _QosIgnoreLocal]:
        if not self._get_ignorelocal(self._ref, byref(self._gc_ignorelocal)):
            raise QosException("Ignorelocal or Qos object invalid.")

        return _PolicyType.IgnoreLocal, _QosIgnoreLocal(self._gc_ignorelocal.value)

    def get_propnames(self) -> List[str]:
        if not self._get_propnames(self._ref, byref(self._gc_propnames_num), byref(self._gc_propnames_names)):
            raise QosException("Propnames or Qos object invalid.")

        names = [None] * self._gc_propnames_num
        for i in range(self._gc_propnames_num):
            names[i] = self._gc_propnames_names[0][i].encode()

        return names

    def get_prop(self, name: str) -> str:
        if not self._get_prop(self._ref, name.encode(), byref(self._gc_prop_get_value)):
            raise QosException("Propname or Qos object invalid.")

        return bytes(self._gc_prop_get_value).decode()

    def get_bpropnames(self) -> List[str]:
        if not self._get_bpropnames(self._ref, byref(self._gc_bpropnames_num), byref(self._gc_bpropnames_names)):
            raise QosException("Propnames or Qos object invalid.")

        names = [None] * self._gc_bpropnames_num
        for i in range(self._gc_bpropnames_num):
            names[i] = self._gc_bpropnames_names[0][i].encode()

        return names

    def get_bprop(self, name: str) -> bytes:
        if not self._get_bprop(self._ref, name.encode(), byref(self._gc_bprop_get_value)):
            raise QosException("Propname or Qos object invalid.")

        return bytes(self._gc_bprop_get_value)

    def set_userdata(self, value: Structure) -> None:
        value_p = cast(byref(value), c_void_p)
        self._set_userdata(self._ref, value_p, sizeof(value))

    def set_topicdata(self, value: Structure) -> None:
        value_p = cast(byref(value), c_void_p)
        self._set_topicdata(self._ref, value_p, sizeof(value))

    def set_groupdata(self, value: Structure) -> None:
        value_p = cast(byref(value), c_void_p)
        self._set_groupdata(self._ref, value_p, sizeof(value))

    def set_durability(self, durability: Tuple[_PolicyType, _QosDurability]) -> None:
        assert(durability[0] == _PolicyType.Durability)
        self._set_durability(self._ref, durability[1].value)

    def set_history(self, history: Tuple[_PolicyType, Tuple[_QosHistory, int]]) -> None:
        assert(history[0] == _PolicyType.History)
        self._set_history(self._ref, history[1][0].value, history[1][1])

    def set_resource_limits(self, limits: Tuple[_PolicyType, Tuple[int, int, int]]) -> None:
        assert(limits[0] == _PolicyType.ResourceLimits)
        self._set_resource_limits(self._ref, *limits[1])

    def set_presentation_access_scope(self, presentation: Tuple[_PolicyType, Tuple[_QosAccessScope, bool, bool]]) -> None:
        assert(presentation[0] == _PolicyType.PresentationAccessScope)
        self._set_presentation_access_scope(self._ref, presentation[1][0].value, presentation[1][1], presentation[1][2])

    def set_lifespan(self, lifespan: Tuple[_PolicyType, int]) -> None:
        assert(lifespan[0] == _PolicyType.Lifespan)
        self._set_lifespan(self._ref, lifespan[1])

    def set_deadline(self, deadline: Tuple[_PolicyType, int]) -> None:
        assert(deadline[0] == _PolicyType.Deadline)
        self._set_deadline(self._ref, deadline[1])

    def set_latency_budget(self, latency_budget: Tuple[_PolicyType, int]) -> None:
        assert(latency_budget[0] == _PolicyType.LatencyBudget)
        self._set_latency_budget(self._ref, latency_budget[1])

    def set_ownership(self, ownership: Tuple[_PolicyType, _QosOwnership]) -> None:
        assert(ownership[0] == _PolicyType.Ownership)
        self._set_ownership(self._ref, ownership[1].value)

    def set_ownership_strength(self, strength: Tuple[_PolicyType, int]) -> None:
        assert(strength[0] == _PolicyType.OwnershipStrength)
        self._set_ownership_strength(self._ref, strength[1])

    def set_liveliness(self, liveliness: Tuple[_PolicyType, Tuple[_QosLiveliness, int]]) -> None:
        assert(liveliness[0] == _PolicyType.Liveliness)
        self._set_liveliness(self._ref, liveliness[1][0].value, liveliness[1][1])

    def set_time_based_filter(self, minimum_separation: Tuple[_PolicyType, int]) -> None:
        assert(minimum_separation[0] == _PolicyType.TimeBasedFilter)
        self._set_time_based_filter(self._ref, minimum_separation[1])

    def set_partitions(self, partitions: Tuple[_PolicyType, List[str]]) -> None:
        assert(partitions[0] == _PolicyType.Partitions)
        ps = [p.encode() for p in partitions[1]]
        p_pt = (c_char_p * len(ps))()
        for i, p in enumerate(ps):
            p_pt[i] = ps[i]
        self._set_partitions(self._ref, len(ps), p_pt)

    def set_reliability(self, reliability: Tuple[_PolicyType, Tuple[_QosReliability, int]]) -> None:
        assert(reliability[0] == _PolicyType.Reliability)
        self._set_reliability(self._ref, reliability[1][0].value, reliability[1][1])

    def set_transport_priority(self, value: Tuple[_PolicyType, int]) -> None:
        assert(value[0] == _PolicyType.TransportPriority)
        self._set_transport_priority(self._ref, value[1])

    def set_destination_order(self, destination_order_kind: Tuple[_PolicyType, _QosDestinationOrder]) -> None:
        assert(destination_order_kind[0] == _PolicyType.DestinationOrder)
        self._set_destination_order(self._ref, destination_order_kind[1].value)

    def set_writer_data_lifecycle(self, autodispose: Tuple[_PolicyType, bool]) -> None:
        assert(autodispose[0] == _PolicyType.WriterDataLifecycle)
        self._set_writer_data_lifecycle(self._ref, autodispose[1])

    def set_reader_data_lifecycle(self, autopurge: Tuple[_PolicyType, Tuple[int, int]]) -> None:
        assert(autopurge[0] == _PolicyType.ReaderDataLifecycle)
        self._set_reader_data_lifecycle(self._ref, *autopurge[1])

    def set_durability_service(self, settings: Tuple[_PolicyType, Tuple[int, _QosHistory, int, int, int, int]]) -> None:
        assert(settings[0] == _PolicyType.DurabilityService)
        self._set_durability_service(self._ref, settings[1][0], settings[1][1].value, settings[1][2], settings[1][3], settings[1][4], settings[1][5])

    def set_ignore_local(self, ignorelocal: Tuple[_PolicyType, _QosIgnoreLocal]) -> None:
        assert(ignorelocal[0] == _PolicyType.IgnoreLocal)
        self._set_ignore_local(self._ref, ignorelocal[1].value)

    def set_prop(self, name: str, value: str) -> None:
        self._set_prop(self._ref, name.encode(), value.encode())

    def unset_prop(self, name: str) -> None:
        self._unset_prop(self._ref, name.encode())

    def set_bprop(self, name: str, value: Structure) -> None:
        self._set_bprop(self._ref, name.encode(), cast(byref(value), c_void_p), sizeof(value))

    def unset_bprop(self, name: str) -> None:
        self._unset_bprop(self._ref, name.encode())

    def _pre_alloc_data_pointers(self):
        self._gc_userdata_size = c_size_t()
        self._gc_userdata_value = c_void_p()
        self._gc_topicdata_size = c_size_t()
        self._gc_topicdata_value = c_void_p()
        self._gc_groupdata_size = c_size_t()
        self._gc_groupdata_value = c_void_p()
        self._gc_durability = dds_durability_t()
        self._gc_history = dds_history_t()
        self._gc_history_depth = c_int32()
        self._gc_max_samples = c_int32()
        self._gc_max_instances = c_int32()
        self._gc_max_samples_per_instance = c_int32()
        self._gc_access_scope = dds_presentation_access_scope_t()
        self._gc_coherent_access = c_bool()
        self._gc_ordered_access = c_bool()
        self._gc_lifespan = dds_duration_t()
        self._gc_deadline = dds_duration_t()
        self._gc_latency_budget = dds_duration_t()
        self._gc_ownership = dds_ownership_t()
        self._gc_ownership_strength = c_int32()
        self._gc_liveliness = dds_liveliness_t()
        self._gc_lease_duration = dds_duration_t()
        self._gc_time_based_filter = dds_duration_t()
        self._gc_partition_num = c_uint32()
        self._gc_partition_names = (POINTER(c_char_p))()
        self._gc_reliability = dds_reliability_t()
        self._gc_max_blocking_time = dds_duration_t()
        self._gc_transport_priority = c_int32()
        self._gc_destination_order = dds_destination_order_t()
        self._gc_writer_autodispose = c_bool()
        self._gc_autopurge_nowriter_samples_delay = dds_duration_t()
        self._gc_autopurge_disposed_samples_delay = dds_duration_t()
        self._gc_durservice_service_cleanup_delay = dds_duration_t()
        self._gc_durservice_history_kind = dds_history_t()
        self._gc_durservice_history_depth = c_int32()
        self._gc_durservice_max_samples = c_int32()
        self._gc_durservice_max_instances = c_int32()
        self._gc_durservice_max_samples_per_instance = c_int32()
        self._gc_ignorelocal = dds_ingnorelocal_t()
        self._gc_propnames_num = c_uint32()
        self._gc_propnames_names = (POINTER(c_char_p))()
        self._gc_prop_get_value = c_char_p()
        self._gc_bpropnames_num = c_uint32()
        self._gc_bpropnames_names = (POINTER(c_char_p))()
        self._gc_bprop_get_value = c_char_p()


    @c_call("dds_create_qos")
    def _create_qos(self) -> dds_qos_p_t:
        pass

    @c_call("dds_delete_qos")
    def _delete_qos(self, qos: dds_qos_p_t) -> None:
        pass


    @c_call("dds_qset_reliability")
    def _set_reliability(self, qos: dds_qos_p_t, reliability_kind: dds_reliability_t, blocking_time: dds_duration_t) -> None:
        pass

    @c_call("dds_qset_durability")
    def _set_durability(self, qos: dds_qos_p_t, durability_kind: dds_durability_t) -> None:
        pass

    @c_call("dds_qset_userdata")
    def _set_userdata(self, qos: dds_qos_p_t, value: c_void_p, size: c_size_t) -> None:
        pass

    @c_call("dds_qset_topicdata")
    def _set_topicdata(self, qos: dds_qos_p_t, value: c_void_p, size: c_size_t) -> None:
        pass

    @c_call("dds_qset_groupdata")
    def _set_groupdata(self, qos: dds_qos_p_t, value: c_void_p, size: c_size_t) -> None:
        pass

    @c_call("dds_qset_history")
    def _set_history(self, qos: dds_qos_p_t, history_kind: dds_history_t, depth: c_int32) -> None:
        pass

    @c_call("dds_qset_resource_limits")
    def _set_resource_limits(self, qos: dds_qos_p_t, max_samples: c_int32, max_instances: c_int32, max_samples_per_instance: c_int32) -> None:
        pass

    @c_call("dds_qset_presentation")
    def _set_presentation_access_scope(self, qos: dds_qos_p_t, access_scope: dds_presentation_access_scope_t, coherent_access: c_bool, ordered_access: c_bool) -> None:
        pass

    @c_call("dds_qset_lifespan")
    def _set_lifespan(self, qos: dds_qos_p_t, lifespan: dds_duration_t) -> None:
        pass

    @c_call("dds_qset_deadline")
    def _set_deadline(self, qos: dds_qos_p_t, deadline: dds_duration_t) -> None:
        pass

    @c_call("dds_qset_latency_budget")
    def _set_latency_budget(self, qos: dds_qos_p_t, latency_budget: dds_duration_t) -> None:
        pass

    @c_call("dds_qset_ownership")
    def _set_ownership(self, qos: dds_qos_p_t, ownership_kind: dds_ownership_t) -> None:
        pass

    @c_call("dds_qset_ownership_strength")
    def _set_ownership_strength(self, qos: dds_qos_p_t, ownership_strength: c_int32) -> None:
        pass

    @c_call("dds_qset_liveliness")
    def _set_liveliness(self, qos: dds_qos_p_t, liveliness_kind: dds_liveliness_t, lease_duration: dds_duration_t) -> None:
        pass

    @c_call("dds_qset_time_based_filter")
    def _set_time_based_filter(self, qos: dds_qos_p_t, minimum_separation: dds_duration_t) -> None:
        pass

    @c_call("dds_qset_partition1")
    def _set_partition(self, qos: dds_qos_p_t, name: c_char_p) -> None:
        pass

    @c_call("dds_qset_partition")
    def _set_partitions(self, qos: dds_qos_p_t, n: c_uint32, ps: POINTER(c_char_p)) -> None:
        pass

    @c_call("dds_qset_transport_priority")
    def _set_transport_priority(self, qos: dds_qos_p_t, value: c_int32) -> None:
        pass

    @c_call("dds_qset_destination_order")
    def _set_destination_order(self, qos: dds_qos_p_t, destination_order_kind: dds_destination_order_t) -> None:
        pass
    
    @c_call("dds_qset_writer_data_lifecycle")
    def _set_writer_data_lifecycle(self, qos: dds_qos_p_t, autodispose: c_bool) -> None:
        pass

    @c_call("dds_qset_reader_data_lifecycle")
    def _set_reader_data_lifecycle(self, qos: dds_qos_p_t, autopurge_nowriter_samples_delay: dds_duration_t, autopurge_disposed_samples_delay: dds_duration_t) -> None:
        pass

    @c_call("dds_qset_durability_service")
    def _set_durability_service(self, qos: dds_qos_p_t, service_cleanup_delay: dds_duration_t, history_kind: dds_history_t, history_depth: c_int32, max_samples: c_int32, max_instances: c_int32, max_samples_per_instance: c_int32) -> None:
        pass

    @c_call("dds_qset_ignorelocal")
    def _set_ignore_local(self, qos: dds_qos_p_t, ingorelocal_kind: dds_ingnorelocal_t) -> None:
        pass

    @c_call("dds_qset_prop")
    def _set_prop(self, qos: dds_qos_p_t, name: c_char_p, value: c_char_p) -> None:
        pass

    @c_call("dds_qunset_prop")
    def _unset_prop(self, qos: dds_qos_p_t, name: c_char_p) -> None:
        pass

    @c_call("dds_qset_bprop")
    def _set_bprop(self, qos: dds_qos_p_t, name: c_char_p, value: c_void_p, size: c_size_t) -> None:
        pass

    @c_call("dds_qunset_bprop")
    def _unset_bprop(self, qos: dds_qos_p_t, name: c_char_p) -> None:
        pass

    @c_call("dds_qget_reliability")
    def _get_reliability(self, qos: dds_qos_p_t, reliability_kind: POINTER(dds_reliability_t), blocking_time: POINTER(dds_duration_t)) -> bool:
        pass

    @c_call("dds_qget_durability")
    def _get_durability(self, qos: dds_qos_p_t, durability_kind: POINTER(dds_durability_t)) -> bool:
        pass

    @c_call("dds_qget_userdata")
    def _get_userdata(self, qos: dds_qos_p_t, value: POINTER(c_void_p), size: POINTER(c_size_t)) -> bool:
        pass

    @c_call("dds_qget_topicdata")
    def _get_topicdata(self, qos: dds_qos_p_t, value: POINTER(c_void_p), size: POINTER(c_size_t)) -> bool:
        pass

    @c_call("dds_qget_groupdata")
    def _get_groupdata(self, qos: dds_qos_p_t, value: POINTER(c_void_p), size: POINTER(c_size_t)) -> bool:
        pass

    @c_call("dds_qget_history")
    def _get_history(self, qos: dds_qos_p_t, history_kind: POINTER(dds_history_t), depth: POINTER(c_int32)) -> bool:
        pass

    @c_call("dds_qget_resource_limits")
    def _get_resource_limits(self, qos: dds_qos_p_t, max_samples: POINTER(c_int32), max_instances: POINTER(c_int32), max_samples_per_instance: POINTER(c_int32)) -> bool:
        pass

    @c_call("dds_qget_presentation")
    def _get_presentation(self, qos: dds_qos_p_t, access_scope: POINTER(dds_presentation_access_scope_t), coherent_access: POINTER(c_bool), ordered_access: POINTER(c_bool)) -> bool:
        pass

    @c_call("dds_qget_lifespan")
    def _get_lifespan(self, qos: dds_qos_p_t, lifespan: POINTER(dds_duration_t)) -> bool:
        pass

    @c_call("dds_qget_deadline")
    def _get_deadline(self, qos: dds_qos_p_t, deadline: POINTER(dds_duration_t)) -> bool:
        pass

    @c_call("dds_qget_latency_budget")
    def _get_latency_budget(self, qos: dds_qos_p_t, latency_budget: POINTER(dds_duration_t)) -> bool:
        pass

    @c_call("dds_qget_ownership")
    def _get_ownership(self, qos: dds_qos_p_t, ownership_kind: POINTER(dds_ownership_t)) -> bool:
        pass

    @c_call("dds_qget_ownership_strength")
    def _get_ownership_strength(self, qos: dds_qos_p_t, strength: POINTER(c_int32)) -> bool:
        pass

    @c_call("dds_qget_liveliness")
    def _get_liveliness(self, qos: dds_qos_p_t, liveliness_kind: POINTER(dds_liveliness_t), lease_duration: POINTER(dds_duration_t)) -> bool:
        pass

    @c_call("dds_qget_time_based_filter")
    def _get_time_based_filter(self, qos: dds_qos_p_t, minimum_separation: POINTER(dds_duration_t)) -> bool:
        pass

    @c_call("dds_qget_partition")
    def _get_partitions(self, qos: dds_qos_p_t, n: POINTER(c_uint32), ps: POINTER(POINTER(c_char_p))) -> bool:
        pass

    @c_call("dds_qget_transport_priority")
    def _get_transport_priority(self, qos: dds_qos_p_t, value: POINTER(c_int32)) -> bool:
        pass

    @c_call("dds_qget_destination_order")
    def _get_destination_order(self, qos: dds_qos_p_t, destination_order_kind: POINTER(dds_destination_order_t)) -> bool:
        pass
    
    @c_call("dds_qget_writer_data_lifecycle")
    def _get_writer_data_lifecycle(self, qos: dds_qos_p_t, autodispose: POINTER(c_bool)) -> bool:
        pass

    @c_call("dds_qget_reader_data_lifecycle")
    def _get_reader_data_lifecycle(self, qos: dds_qos_p_t, autopurge_nowriter_samples_delay: POINTER(dds_duration_t), autopurge_disposed_samples_delay: POINTER(dds_duration_t)) -> bool:
        pass

    @c_call("dds_qget_durability_service")
    def _get_durability_service(self, qos: dds_qos_p_t, service_cleanup_delay: POINTER(dds_duration_t), history_kind: POINTER(dds_history_t), history_depth: POINTER(c_int32), max_samples: POINTER(c_int32), max_instances: POINTER(c_int32), max_samples_per_instance: POINTER(c_int32)) -> bool:
        pass

    @c_call("dds_qget_ignorelocal")
    def _get_ignorelocal(self, qos: dds_qos_p_t, ingorelocal_kind: POINTER(dds_ingnorelocal_t)) -> bool:
        pass

    @c_call("dds_qget_prop")
    def _get_prop(self, qos: dds_qos_p_t, name: POINTER(c_char_p), value: POINTER(c_char_p)) -> bool:
        pass

    @c_call("dds_qget_bprop")
    def _get_bprop(self, qos: dds_qos_p_t, name: POINTER(c_char_p), value: POINTER(c_char_p)) -> bool:
        pass

    @c_call("dds_qget_propnames")
    def _get_propnames(self,  qos: dds_qos_p_t, size: POINTER(c_uint32), names: POINTER(POINTER(c_char_p))) -> bool:
        pass

    @c_call("dds_qget_bpropnames")
    def _get_bpropnames(self,  qos: dds_qos_p_t, size: POINTER(c_uint32), names: POINTER(POINTER(c_char_p))) -> bool:
        pass

    @c_call("dds_qos_equal")
    def _eq(self, qos_a: dds_qos_p_t, qos_b: dds_qos_p_t) -> bool:
        pass
    
# Set DDS qos type
DDS.qos_type = Qos