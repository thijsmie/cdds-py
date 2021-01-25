from ctypes import Structure, POINTER, c_char, c_size_t, c_uint, c_uint32, c_bool, c_char_p, c_void_p, c_uint16
from cdds.internal.cfunc import c_callable
from cdds.internal.clib import load_library


class ddsrt_atomic_uint32_t(Structure):
    _fields_ = [('v', c_uint32)]


class ddsi_keyhash(Structure):
    _fields_ = [('value', c_char * 16)]


ddsi_serdata_kind = c_uint


# Forward declarators
class ddsi_sertype_ops(Structure):
    pass


class ddsi_serdata_ops(Structure):
    pass


class ddsi_sertype(Structure):
    pass


class ddsi_serdata(Structure):
    pass


ddsrt_msg_iovlen_t = c_size_t
ddsrt_iovlen_t = c_size_t

class ddsrt_iovec(Structure):
    _fields_ = [
        ("iov_len", ddsrt_iovlen_t),
        ("iov_base", c_void_p)
    ]


ddsi_sertype_free_t = c_callable(None, [POINTER(ddsi_sertype)])
ddsi_sertype_zero_samples_t = c_callable(None, [POINTER(ddsi_sertype), c_void_p, c_size_t])
ddsi_sertype_realloc_samples_t = c_callable(None, [POINTER(c_void_p), POINTER(ddsi_sertype), c_void_p, c_size_t, c_size_t])
ddsi_sertype_free_samples_t = c_callable(None, [POINTER(ddsi_sertype), POINTER(c_void_p), c_void_p, c_uint])
ddsi_sertype_equal_t = c_callable(c_bool, [POINTER(ddsi_sertype), POINTER(ddsi_sertype)])
ddsi_sertype_hash_t = c_callable(c_uint32, [POINTER(ddsi_sertype)])
ddsi_sertype_typeid_hash_t = c_callable(c_bool, [POINTER(ddsi_sertype), c_char_p])
ddsi_sertype_serialized_size_t = c_callable(None, [POINTER(ddsi_sertype), POINTER(c_size_t)])
ddsi_sertype_serialize_t = c_callable(None, [POINTER(ddsi_sertype), POINTER(c_size_t), c_char_p])
ddsi_sertype_deserialize_t = c_callable(c_bool, [c_void_p, POINTER(ddsi_sertype), c_size_t, c_char_p, POINTER(c_size_t)])
ddsi_sertype_assignable_from_t = c_callable(c_bool, [POINTER(ddsi_sertype), POINTER(ddsi_sertype)])


ddsi_serdata_eqkey_t = c_callable(bool, [POINTER(ddsi_serdata), POINTER(ddsi_serdata)])
ddsi_serdata_size_t = c_callable(c_uint32, [POINTER(ddsi_serdata)])
ddsi_serdata_from_ser_t = c_callable(POINTER(ddsi_serdata), [POINTER(ddsi_sertype), ddsi_serdata_kind, POINTER(nn_rdata), c_size_t])
ddsi_serdata_from_ser_iov_t = c_callable(POINTER(ddsi_serdata), [POINTER(ddsi_sertype), ddsi_serdata_kind, POINTER(nn_rdata), c_size_t])
ddsi_serdata_from_keyhash_t = c_callable(POINTER(ddsi_serdata), [POINTER(ddsi_sertype), POINTER(ddsi_keyhash)])
ddsi_serdata_from_sample_t = c_callable(POINTER(ddsi_serdata), [POINTER(ddsi_sertype), ddsi_serdata_kind, c_void_p])
ddsi_serdata_to_ser_t = c_callable(None, [POINTER(ddsi_serdata), c_size_t, c_size_t, c_void_p])
ddsi_serdata_to_ser_ref_t = c_callable(POINTER(ddsi_serdata), [POINTER(ddsi_serdata), c_size_t, c_size_t, POINTER(ddsrt_iovec)])
ddsi_serdata_to_ser_unref_t = c_callable(None, [POINTER(ddsi_serdata), POINTER(ddsrt_iovec)])
ddsi_serdata_to_sample_t = c_callable(c_bool, [POINTER(ddsi_serdata), c_void_p, POINTER(c_void_p), c_void_p])
ddsi_serdata_to_untyped_t = c_callable(POINTER(ddsi_serdata), [POINTER(ddsi_serdata)])
ddsi_serdata_untyped_to_sample_t = c_callable(c_bool, [POINTER(ddsi_sertype), POINTER(ddsi_serdata), c_void_p, POINTER(c_void_p), c_void_p])
ddsi_serdata_free_t = c_callable(None, [POINTER(ddsi_serdata)])
ddsi_serdata_print_t = c_callable(c_size_t, [POINTER(ddsi_sertype), POINTER(ddsi_serdata), c_char_p, c_size_t])
ddsi_serdata_get_keyhash_t = c_callable(None, [POINTER(ddsi_serdata), POINTER(ddsi_keyhash), c_bool])


# Finalize
ddsi_sertype_ops._fields_ = [
    ('version', c_void_p),
    ('arg', c_void_p),
    ('free', ddsi_sertype_free_t),
    ('zero_samples', ddsi_sertype_zero_samples_t),
    ('realloc_samples', ddsi_sertype_realloc_samples_t),
    ('free_samples', ddsi_sertype_free_samples_t),
    ('equal', ddsi_sertype_equal_t),
    ('hash', ddsi_sertype_hash_t),
    ('typeid_hash', ddsi_sertype_typeid_hash_t),
    ('serialized_size', ddsi_sertype_serialized_size_t),
    ('serialize', ddsi_sertype_serialize_t),
    ('deserialize', ddsi_sertype_deserialize_t),
    ('assignable_from', ddsi_sertype_assignable_from_t)
]

ddsi_serdata_ops._fields_ = [
    ('eqkey', ddsi_serdata_eqkey_t),
    ('get_size', ddsi_serdata_size_t),
    ('from_ser', ddsi_serdata_from_ser_t),
    ('from_ser_iov', ddsi_serdata_from_ser_iov_t),
    ('from_keyhash', ddsi_serdata_from_keyhash_t),
    ('from_sample', ddsi_serdata_from_sample_t),
    ('to_ser', ddsi_serdata_to_ser_t),
    ('to_ser_ref', ddsi_serdata_to_ser_ref_t),
    ('to_ser_unref', ddsi_serdata_to_ser_unref_t),
    ('to_sample', ddsi_serdata_to_sample_t),
    ('to_untyped', ddsi_serdata_to_untyped_t),
    ('untyped_to_sample', ddsi_serdata_untyped_to_sample_t),
    ('free', ddsi_serdata_free_t),
    ('print', ddsi_serdata_print_t),
    ('get_keyhash', ddsi_serdata_get_keyhash_t)
]


ddsi_sertype._fields_ = [
    ('ops', POINTER(ddsi_sertype_ops)),
    ('serdata_ops', POINTER(ddsi_serdata_ops)),
    ('serdata_basehash', c_uint32),
    ('typekind_no_key', c_bool),
    ('type_name', c_char_p),
    ('gv', c_void_p),
    ('flags_refc', ddsrt_atomic_uint32_t),
    ('wrapped_sertopic', c_void_p)
]

ddsi_serdata._fields_ = [
    ('ops', POINTER(ddsi_serdata_ops)),
    ('hash', c_uint32),
    ('refc', ddsrt_atomic_uint32_t),
    ('kind', ddsi_serdata_kind),
    ('topic', POINTER(ddsi_sertype))
]