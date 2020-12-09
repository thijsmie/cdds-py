import ctypes as ct
from uuid import UUID


dds_entity_t = ct.c_int32
dds_time_t = ct.c_int64
dds_duration_t = ct.c_int64
dds_instance_handle_t = ct.c_int64
dds_domainid_t = ct.c_uint32
dds_sample_state_t = ct.c_int
dds_view_state_t = ct.c_int
dds_instance_state_t = ct.c_int
dds_reliability_t = ct.c_int
dds_durability_t = ct.c_int
dds_history_t = ct.c_int
dds_presentation_access_scope_t = ct.c_int
dds_ingnorelocal_t = ct.c_int
dds_ownership_t = ct.c_int
dds_liveliness_t = ct.c_int
dds_destination_order_t = ct.c_int
dds_qos_p_t = ct.c_void_p
dds_attach_t = ct.c_void_p
dds_listener_p_t = ct.c_void_p
dds_topic_descriptor_p_t = ct.c_void_p
dds_return_t = ct.c_int32

class SampleInfo(ct.Structure):
    _fields_ = [('sample_state', ct.c_uint),
                ('view_state', ct.c_uint),
                ('instance_state', ct.c_uint),
                ('valid_data', ct.c_bool),
                ('source_timestamp', ct.c_int64),
                ('instance_handle', ct.c_uint64),
                ('pubblication_handle', ct.c_uint64),
                ('disposed_generation_count', ct.c_uint32),
                ('no_writer_generation_count', ct.c_uint32),
                ('sample_rank', ct.c_uint32),
                ('generation_rank', ct.c_uint32),
                ('absolute_generation_rank', ct.c_uint32)]


class dds_inconsistent_topic_status_t(ct.Structure):
    _fields_ = [('total_count', ct.c_uint32),
                ('total_count_change', ct.c_int32)]


class dds_liveliness_lost_status_t(ct.Structure):
    _fields_ = [('total_count', ct.c_uint32),
                ('total_count_change', ct.c_int32)]

class dds_liveliness_changed_status_t(ct.Structure):
    _fields_ = [('alive_count', ct.c_uint32),
                ('not_alive_count', ct.c_uint32),
                ('alive_count_change', ct.c_int32),
                ('not_alive_count_change', ct.c_int32)]

class dds_offered_deadline_missed_status_t(ct.Structure):
    _fields_ = [('total_count', ct.c_uint32),
                ('total_count_change', ct.c_int32),
                ('last_instance_handle', dds_instance_handle_t)]


class dds_guid_t(ct.Structure):
    _fields_ = [('v', ct.c_uint8 * 16)]

    def as_python_guid(self) -> UUID:
        return UUID(bytes(self.v))