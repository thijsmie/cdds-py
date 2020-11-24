from cdds.core import DDS
from cdds.internal import c_call, dds_qos_p_t, dds_return_t, dds_reliability_t, dds_durability_t, dds_duration_t, dds_history_t, \
    dds_presentation_access_scope_t, dds_ownership_t, dds_liveliness_t, dds_destination_order_t, dds_ingnorelocal_t
from ctypes import c_void_p, c_int32, c_char_p, POINTER, c_size_t, c_uint32, c_bool, cast, byref, sizeof, Structure
from enum import Enum
from typing import Tuple, Optional, List, Any



class QosReliability(Enum):
    BestEffort = 0
    Reliable = 1


class QosDurability(Enum):
    Volatile = 0
    TransientLocal = 1
    Transient = 2
    Persistent = 3


class QosHistory(Enum):
    KeepLast = 0
    KeepAll = 1


class QosAccessScope(Enum):
    Instance = 0
    Topic = 1
    Group = 2


class QosOwnership(Enum):
    Shared = 0
    Exclusive = 1


class QosLiveliness(Enum):
    Automatic = 0
    ManualByParticipant = 1
    ManualByTopic = 2


class QosDestinationOrder(Enum):
    ByReceptionTimestamp = 0
    BySourceTimestamp = 1


class QosIgnoreLocal(Enum):
    Nothing = 0
    Participant = 1
    Process = 2


class QosException(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"[Qos] {self.msg}"

    __repr__ = __str__


class Qos(DDS):
    _qosses = {}

    def __init__(self, **kwargs):
        super().__init__(self._create_qos())
        self._qosses[self._ref] = self

        self._pre_alloc_data_pointers()

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

    @classmethod
    def get_qos(cls, id):
        return cls._qosses.get(id)

    def __del__(self):
        self._delete_qos(self._ref)

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

    @property
    def durability(self) -> QosDurability:
        if not self._get_durability(self._ref, byref(self._gc_durability)):
            raise QosException("Durability or Qos object invalid.")

        return QosDurability(int(self._gc_durability))

    @property
    def history(self) -> Tuple[QosHistory, int]:
        if not self._get_history(self._ref, byref(self._gc_history), byref(self._gc_history_depth)):
            raise QosException("History or Qos object invalid.")

        return QosHistory(int(self._gc_history)), int(self._gc_history_depth)

    @property
    def resource_limits(self) -> Tuple[int, int, int]:
        if not self._get_resource_limits(self._ref, byref(self._gc_max_samples), byref(self._gc_max_instances), byref(self._gc_max_samples_per_instance)):
            raise QosException("Resource limits or Qos object invalid.")

        return int(self._gc_max_samples), int(self._gc_max_instances), int(self._gc_max_samples_per_instance)

    @property
    def presentation(self) -> Tuple[QosAccessScope, bool, bool]:
        if not self._get_presentation(self._ref, byref(self._gc_access_scope), byref(self._gc_coherent_access), byref(self._gc_ordered_access)):
            raise QosException("Presentation or Qos object invalid.")
        
        return QosAccessScope(int(self._gc_access_scope)), bool(self._gc_coherent_access), bool(self._gc_ordered_access)

    @property
    def lifespan(self) -> int:
        if not self._get_lifespan(self._ref, byref(self._gc_lifespan)):
            raise QosException("Lifespan or Qos object invalid.")

        return int(self._gc_lifespan)

    @property
    def deadline(self) -> int:
        if not self._get_deadline(self._ref, byref(self._gc_deadline)):
            raise QosException("Deadline or Qos object invalid.")

        return int(self._gc_deadline)

    @property
    def latency_budget(self) -> int:
        if not self._get_latency_budget(self._ref, byref(self._gc_latency_budget)):
            raise QosException("Deadline or Qos object invalid.")

        return int(self._gc_latency_budget)

    @property
    def ownership(self) -> QosOwnership:
        if not self._get_ownership(self._ref, byref(self._gc_ownership)):
            raise QosException("Ownership or Qos object invalid.")

        return QosOwnership(int(self._gc_ownership))

    @property
    def ownership_strength(self) -> int:
        if not self._get_ownership_strength(self._ref, byref(self._gc_ownership_strength)):
            raise QosException("Ownership strength or Qos object invalid.")

        return int(self._gc_ownership_strength)

    @property
    def liveliness(self) -> Tuple[QosLiveliness, int]:
        if not self._get_liveliness(self._ref, byref(self._gc_liveliness), byref(self._gc_lease_duration)):
            raise QosException("Liveliness or Qos object invalid.")

        return QosLiveliness(int(self._gc_liveliness)), int(self._gc_lease_duration)

    @property
    def time_based_filter(self) -> int:
        if not self._get_time_based_filter(self._ref, byref(self._gc_time_based_filter)):
            raise QosException("Time Based Filter or Qos object invalid.")

        return int(self._gc_time_based_filter)

    @property
    def partitions(self) -> List[str]:
        if not self._get_partitions(self._ref, byref(self._gc_partition_num), byref(self._gc_partition_names)):
            raise QosException("Partition or Qos object invalid.")

        names = [None] * self._gc_partition_num
        for i in range(self._gc_partition_num):
            names[i] = bytes(self._gc_partition_names[0][i]).decode()

        return names

    @property
    def reliability(self) -> Tuple[QosReliability, int]:
        if not self._get_reliability(self._ref, byref(self._gc_reliability), byref(self._gc_max_blocking_time)):
            raise QosException("Reliability or Qos object invalid.")

        return QosReliability(int(self._gc_reliability)), int(self._gc_max_blocking_time)

    @property
    def transport_priority(self) -> int:
        if not self._get_transport_priority(self._ref, byref(self._gc_transport_priority)):
            raise QosException("Transport Priority or Qos object invalid.")

        return int(self._gc_transport_priority)

    @property
    def destination_order(self) -> QosDestinationOrder:
        if not self._get_destination_order(self._ref, byref(self._gc_destination_order)):
            raise QosException("Destination Order or Qos object invalid.")

        return QosDestinationOrder(int(self._gc_destination_order))

    @property
    def writer_data_lifecycle(self) -> bool:
        if not self._get_writer_data_lifecycle(self._ref, byref(self._gc_writer_autodispose)):
            raise QosException("Writer Data Lifecycle or Qos object invalid.")

        return bool(self._gc_writer_autodispose)

    @property
    def reader_data_lifecycle(self) -> Tuple[int, int]:
        if not self._get_reader_data_lifecycle(self._ref, byref(self._gc_autopurge_nowriter_samples_delay), byref(self._gc_autopurge_disposed_samples_delay)):
            raise QosException("Reader Data Lifecycle or Qos object invalid.")

        return int(self._gc_autopurge_nowriter_samples_delay), int(self._gc_autopurge_disposed_samples_delay)

    @property
    def durability_service(self) -> Tuple[int, QosHistory, int, int, int, int]:
        if not self._get_durability_service(self._ref, 
            byref(self._gc_durservice_service_cleanup_delay), 
            byref(self._gc_durservice_history_kind), 
            byref(self._gc_durservice_history_depth), 
            byref(self._gc_durservice_max_samples), 
            byref(self._gc_durservice_max_instances), 
            byref(self._gc_durservice_max_samples_per_instance)):
            raise QosException("Durability Service or Qos object invalid.")

        return int(self._gc_durservice_service_cleanup_delay), QosHistory(int(self._gc_durservice_history_kind)), \
             int(self._gc_durservice_service_cleanup_delay), int(self._gc_durservice_service_cleanup_delay), \
             int(self._gc_durservice_service_cleanup_delay)

    @property
    def ignorelocal(self) -> bool:
        if not self._get_ignorelocal(self._ref, byref(self._gc_ignorelocal)):
            raise QosException("Ignorelocal or Qos object invalid.")

        return bool(self._gc_ignorelocal)

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

    @durability.setter
    def durability(self, durability: QosDurability) -> None:
        self._set_durability(self._ref, durability.value)

    @history.setter
    def history(self, history: Tuple[QosHistory, int]) -> None:
        self._set_history(self._ref, history[0].value, history[1])

    @resource_limits.setter
    def resource_limits(self, limits: Tuple[int, int, int]) -> None:
        self._set_resource_limits(self._ref, *limits)

    @presentation.setter
    def presentation(self, presentation: Tuple[QosAccessScope, bool, bool]) -> None:
        self._set_presentation(self._ref, presentation[0].value, presentation[1], presentation[2])

    @lifespan.setter
    def lifespan(self, lifespan: int) -> None:
        self._set_lifespan(self._ref, lifespan)

    @deadline.setter
    def deadline(self, deadline: int) -> None:
        self._set_deadline(self._ref, deadline)

    @latency_budget.setter
    def latency_budget(self, latency_budget: int) -> None:
        self._set_latency_budget(self._ref, latency_budget)

    @ownership.setter
    def ownership(self, ownership: QosOwnership) -> None:
        self._set_ownership(self._ref, ownership.value)

    @ownership_strength.setter
    def ownership_strength(self, strength: int) -> None:
        self._set_ownership_strength(self._ref, strength)

    @liveliness.setter
    def liveliness(self, liveliness: Tuple[QosLiveliness, int]) -> None:
        self._set_liveliness(self._ref, liveliness[0].value, liveliness[1])

    @time_based_filter.setter
    def time_based_filter(self, minimum_separation: int) -> None:
        self._set_time_based_filter(self._ref, minimum_separation)

    @partitions.setter
    def partitions(self, partitions: List[str]):
        ps = [p.encode() for p in partitions]
        self._set_partitions(self._ref, len(ps), ps)

    @reliability.setter
    def reliabilty(self, reliability: Tuple[QosReliability, int]) -> None:
        self._set_reliability(self._ref, reliability[0].value, reliability[1])

    @transport_priority.setter
    def transport_priority(self, value: int) -> None:
        self._set_transport_priority(self._ref, value)

    @destination_order.setter
    def destination_order(self, destination_order_kind: QosDestinationOrder) -> None:
        self._set_destination_order(self._ref, destination_order_kind.value)

    @writer_data_lifecycle.setter
    def writer_data_lifecycle(self, autodispose: bool) -> None:
        self._set_writer_data_lifecycle(self._ref, autodispose)

    @reader_data_lifecycle.setter
    def reader_data_lifecycle(self, autopurge: Tuple[int, int]) -> None:
        self._set_reader_data_lifecycle(self._ref, *autopurge)

    @durability_service.setter
    def durability_service(self, settings: Tuple[int, QosHistory, int, int, int, int]) -> None:
        self._set_durability_service(self._ref, settings[0], settings[1].value, settings[2], settings[3], settings[4], settings[5])

    @ignorelocal.setter
    def ignorelocal(self, ingnore_local: QosIgnoreLocal) -> None:
        self._set_ignorelocal(self._ref, ingnore_local.value)

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
        self._gc_ownership_strength = dds_duration_t()
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
        self._gc_ignorelocal = c_bool()
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
    def _set_presentation(self, qos: dds_qos_p_t, access_scope: dds_presentation_access_scope_t, coherent_access: c_bool, ordered_access: c_bool) -> None:
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
    def _set_ignorelocal(self, qos: dds_qos_p_t, ingorelocal_kind: dds_ingnorelocal_t) -> None:
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
    
# Set DDS qos type
DDS.qos_type = Qos