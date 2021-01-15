from ctypes import Structure, POINTER, c_size_t, c_uint32, c_bool, c_char_p, c_void_p
from cdds.internal.cfunc import c_callable


class ddsrt_atomic_uint32_t:
    _fields_ = [('v', c_uint32)]


# Forward declarators
class ddsi_sertopic_ops(Structure):
    pass


class ddsi_serdata_ops(Structure):
    pass


class ddsi_sertopic(Structure):
    pass


class ddsi_serdata(Structure):
    pass


class ddsi_serdata_kind(Structure):
    pass


class nn_rdata(Structure):
    pass


class ddsrt_iov


ddsi_serdata_eqkey_t = c_callable(bool, [POINTER(ddsi_serdata), POINTER(ddsi_serdata)])
ddsi_serdata_size_t = c_callable(c_uint32, [POINTER(ddsi_serdata)])
ddsi_serdata_from_ser_t = c_callable(POINTER(ddsi_serdata), [POINTER(ddsi_sertopic), ddsi_serdata_kind, POINTER(nn_rdata), c_size_t])
ddsi_serdata_from_ser_iov_t = c_callable(POINTER(ddsi_serdata), [POINTER(ddsi_sertopic), ddsi_serdata_kind, POINTER(nn_rdata), c_size_t])
ddsi_serdata_from_keyhash_t
ddsi_serdata_from_sample_t
ddsi_serdata_to_ser_t
ddsi_serdata_to_ser_ref_t
ddsi_serdata_to_ser_unref_t
ddsi_serdata_to_sample_t
ddsi_serdata_to_topicless_t
ddsi_serdata_topicless_to_sample_t
ddsi_serdata_free_t
ddsi_serdata_print_t
ddsi_serdata_get_keyhash_t


# Finalize
ddsi_sertopic_ops._fields_ = []

ddsi_serdata_ops._fields_ = []


ddsi_sertopic._fields_ = [
    ('ops', POINTER(ddsi_serdata_ops)),
    ('serdata_ops', POINTER(ddsi_serdata_ops)),
    ('serdata_basehash', c_uint32),
    ('topickind_no_key', c_bool),
    ('name', c_char_p),
    ('type_name', c_char_p),
    ('gv', c_void_p),
    ('refc', ddsrt_atomic_uint32_t)
]