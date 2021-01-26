/*
 * Copyright(c) 2020 ADLINK Technology Limited and others
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0, or the Eclipse Distribution License
 * v. 1.0 which is available at
 * http://www.eclipse.org/org/documents/edl-v10.php.
 *
 * SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause
 */

#include <Python.h>

#include <stdlib.h>
#include <string.h>
#include <stdio.h>


#include "dds/dds.h"

#include "dds/ddsrt/endian.h"
#include "dds/ddsrt/md5.h"
#include "dds/ddsi/q_radmin.h"
#include "dds/ddsi/ddsi_serdata.h"
#include "dds/ddsi/ddsi_sertype.h"


void quickprint(const char* prefix, PyObject* self)
{
    PyObject* repr = PyObject_Repr(self);
    PyObject* str = PyUnicode_AsEncodedString(repr, "utf-8", "~E~");
    const char *bytes = PyBytes_AS_STRING(str);

    printf("%s: %s\n", prefix, bytes);

    Py_XDECREF(repr);
    Py_XDECREF(str);
}


typedef struct ddsi_serdata ddsi_serdata_t;
typedef struct ddsi_sertype ddsi_sertype_t;


typedef struct ddspy_sertype {
    ddsi_sertype_t my_c_type;
    PyObject* my_py_type;
    PyObject* deserialize_attr;
    PyObject* serialize_attr;
    PyObject* key_calc_attr;
    PyObject* keyhash_calc_attr;
    bool key_maxsize_bigger_16;
} ddspy_sertype_t;


typedef struct ddspy_serdata {
    ddsi_serdata_t c_data;
    PyObject* sample;
    void* data;
    size_t data_size;
    ddsi_keyhash_t key;
    bool hash_populated;
} ddspy_serdata_t;

typedef struct ddspy_sample_container {
    PyObject* sample;
} ddspy_sample_container_t;


static inline ddspy_sertype_t* sertype(ddspy_serdata_t *this)
{
    return (ddspy_sertype_t*) (this->c_data.type);
}

static inline const ddspy_sertype_t* csertype(const ddspy_serdata_t *this)
{
    return (const ddspy_sertype_t*) (this->c_data.type);
}

static inline ddspy_serdata_t* serdata(ddsi_serdata_t *this)
{
    return (ddspy_serdata_t*) (this);
}

static inline const ddspy_serdata_t* cserdata(const ddsi_serdata_t *this)
{
    return (const ddspy_serdata_t*) (this);
}

PyObject *memory_as_pybuffer(void *ptr, Py_ssize_t buf_len) {
    Py_buffer pybuf;
    Py_ssize_t shape[] = {buf_len};

    // This is not a copy!
    int ret = PyBuffer_FillInfo(&pybuf, NULL, ptr, buf_len, 1, PyBUF_SIMPLE);
    if (ret!=0)
    	return NULL;
    pybuf.format = "B";
    pybuf.shape = shape;
    return PyMemoryView_FromBuffer(&pybuf);
}

ddspy_serdata_t *ddspy_serdata_new(const struct ddsi_sertype* type, enum ddsi_serdata_kind kind, size_t data_size)
{
    ddspy_serdata_t *new = (ddspy_serdata_t*) malloc(sizeof(ddspy_serdata_t));
    ddsi_serdata_init((ddsi_serdata_t*) new, type, kind);

    new->data = malloc(data_size);
    new->data_size = data_size;
    new->hash_populated = false;
    new->sample = NULL;

    return new;
}

void ddspy_serdata_ensure_sample(ddspy_serdata_t* this)
{
    if (this->sample)
        return;

    PyGILState_STATE state = PyGILState_Ensure();

    PyObject* arglist = Py_BuildValue("(O)", memory_as_pybuffer(this->data, this->data_size));
    PyObject* result = PyObject_CallObject(sertype(this)->deserialize_attr, arglist);
    Py_INCREF(result);
    this->sample = result;

    quickprint("Deserialized", result);

    PyGILState_Release(state);
}

void ddspy_serdata_populate_hash(ddspy_serdata_t* this)
{
    if (this->hash_populated) {
        printf("Already populated\n");
        return;
    }

    if (csertype(this)->keyhash_calc_attr == NULL) {
        printf("No keyhash prop\n");
        return;
    }

    ddspy_serdata_ensure_sample(this);

    /// Make calls into python possible.
    PyGILState_STATE state = PyGILState_Ensure();

    PyObject* arglist = Py_BuildValue("(O)", this->sample);
    PyObject* result = PyObject_CallObject(sertype(this)->keyhash_calc_attr, arglist);
    Py_DECREF(arglist);

    if (result == NULL) {
        // Error condition: This is when python has set an error code, the keyhash is unfilled.
        // We won't set hash_populated, but we have to start the python interpreter back up
        PyGILState_Release(state);
        assert(0);
        return;
    }

    /// This is not a copy
    const char* buf = PyBytes_AsString(result);
    int size = PyBytes_Size(result);

    if (size != 16) {
        // Error condition: Python did not give us 16 bytes exactly
        // We won't set hash_populated, but we have to start the python interpreter back up
        PyGILState_Release(state);
        assert(0);
        return;
    }

    memcpy(this->key.value, buf, 16);
    memcpy(&(this->c_data.hash), buf, 4);

    PyGILState_Release(state);
    this->hash_populated = true;
}

bool serdata_eqkey(const struct ddsi_serdata* a, const struct ddsi_serdata* b)
{
    return 0 == memcmp(cserdata(a)->key.value, cserdata(b)->key.value, 16);
}

uint32_t serdata_size(const struct ddsi_serdata* dcmn)
{
    return (uint32_t) cserdata(dcmn)->data_size;
}

ddsi_serdata_t *serdata_from_ser(
  const struct ddsi_sertype* type,
  enum ddsi_serdata_kind kind,
  const struct nn_rdata* fragchain, size_t size)
{
    ddspy_serdata_t *d = ddspy_serdata_new(type, size, kind);

    uint32_t off = 0;
    assert(fragchain->min == 0);
    assert(fragchain->maxp1 >= off);    //CDR header must be in first fragment

    unsigned char* cursor = d->data;
    while (fragchain) {
        if (fragchain->maxp1 > off) {
            //only copy if this fragment adds data
            const unsigned char* payload =
                NN_RMSG_PAYLOADOFF(fragchain->rmsg, NN_RDATA_PAYLOAD_OFF(fragchain));
            const unsigned char* src = payload + off - fragchain->min;
            size_t n_bytes = fragchain->maxp1 - off;
            memcpy(cursor, src, n_bytes);
            cursor += n_bytes;
            off = fragchain->maxp1;
            assert(off <= size);
        }
        fragchain = fragchain->nextfrag;
    }

    switch (kind)
    {
    case SDK_KEY:
        assert(0); //ddspy_serdata_key_read(d);
        break;
    case SDK_DATA:
        ddspy_serdata_ensure_sample(d);
        break;
    case SDK_EMPTY:
        assert(0);
    }

    ddspy_serdata_populate_hash(d);

    return (ddsi_serdata_t*) d;
}

ddsi_serdata_t *serdata_from_ser_iov(
  const struct ddsi_sertype* type,
  enum ddsi_serdata_kind kind,
  ddsrt_msg_iovlen_t niov,
  const ddsrt_iovec_t* iov,
  size_t size)
{
    ddspy_serdata_t *d = ddspy_serdata_new(type, size, kind);

    size_t off = 0;
    unsigned char* cursor = d->data;
    for (ddsrt_msg_iovlen_t i = 0; i < niov && off < size; i++)
    {
        size_t n_bytes = iov[i].iov_len;
        if (n_bytes + off > size) n_bytes = size - off;
        memcpy(cursor, iov[i].iov_base, n_bytes);
        cursor += n_bytes;
        off += n_bytes;
    }

    switch (kind)
    {
    case SDK_KEY:
        assert(0); //ddspy_serdata_key_read(d);
        break;
    case SDK_DATA:
        ddspy_serdata_ensure_sample(d);
        break;
    case SDK_EMPTY:
        assert(0);
    }

    ddspy_serdata_populate_hash(d);

    return (ddsi_serdata_t*) d;
}

ddsi_serdata_t *serdata_from_keyhash(
  const struct ddsi_sertype* topic,
  const struct ddsi_keyhash* keyhash)
{
  (void)keyhash;
  (void)topic;
  //replace with (if key_size_max <= 16) then populate the data class with the key hash (key_read)
  // TODO
  return NULL;
}


ddsi_serdata_t *serdata_from_sample(
  const ddsi_sertype_t* type,
  enum ddsi_serdata_kind kind,
  const void* sample)
{
    ddspy_sample_container_t *container = (ddspy_sample_container_t*) sample;

    /// If there is no PyObject in the container this is not possible.
    assert(container->sample);

    /// Make calls into python possible.
    PyGILState_STATE state = PyGILState_Ensure();

    ddspy_serdata_t *d;
    switch(kind)
    {
        case SDK_DATA:
        {
            PyObject* arglist = Py_BuildValue("(O)", container->sample);
            PyObject* result = PyObject_CallObject(((const ddspy_sertype_t*) type)->serialize_attr, arglist);
            Py_DECREF(arglist);

            if (result == NULL) {
                // Error condition: This is when python has set an error code, the keyhash is unfilled.
                // We won't set hash_populated, but we have to start the python interpreter back up
                PyGILState_Release(state);
                return NULL;
            }

            /// This is not a copy
            const char* buf = PyBytes_AsString(result);
            int size = PyBytes_Size(result);

            d = ddspy_serdata_new(type, kind, size + 4);
            memcpy(d->data + 4, buf, size);
            Py_DECREF(result);
        }
        break;
        case SDK_KEY:
        {
            PyObject* arglist = Py_BuildValue("(O)", container->sample);
            PyObject* result = PyObject_CallObject(((const ddspy_sertype_t*) type)->key_calc_attr, arglist);
            quickprint("serdata_from_sample-sdk_key-result", result);
            Py_DECREF(arglist);

            if (result == NULL) {
                // Error condition: This is when python has set an error code, the keyhash is unfilled.
                // We won't set hash_populated, but we have to start the python interpreter back up
                PyGILState_Release(state);
                return NULL;
            }

            /// This is not a copy
            const char* buf = PyBytes_AsString(result);
            int size = PyBytes_Size(result);

            d = ddspy_serdata_new(type, kind, size + 4);
            memcpy(d->data + 4, buf, size);
            Py_DECREF(result);
        }
        break;
        default:
        case SDK_EMPTY:
            assert(0);
    }

    Py_IncRef(container->sample);
    d->sample = container->sample;
    PyGILState_Release(state);

    memset(d->data, 0x0, 4);
    if (DDSRT_ENDIAN == DDSRT_LITTLE_ENDIAN)
        memset(d->data + 1, 0x1, 1);

    ddspy_serdata_populate_hash(d);
    return (ddsi_serdata_t*) d;
}


void serdata_to_ser(const ddsi_serdata_t* dcmn, size_t off, size_t sz, void* buf)
{
    memcpy(buf, cserdata(dcmn)->data + off, sz);
}

ddsi_serdata_t *serdata_to_ser_ref(
  const struct ddsi_serdata* dcmn, size_t off,
  size_t sz, ddsrt_iovec_t* ref)
{
    ref->iov_base = cserdata(dcmn)->data + off;
    ref->iov_len = sz;
    return ddsi_serdata_ref(dcmn);
}

void serdata_to_ser_unref(struct ddsi_serdata* dcmn, const ddsrt_iovec_t* ref)
{
    (void)ref;    // unused
    ddsi_serdata_unref(dcmn);
}

bool serdata_to_sample(
  const ddsi_serdata_t* dcmn, void* sample, void** bufptr,
  void* buflim)
{
    (void)bufptr;
    (void)buflim;

    ddspy_sample_container_t *container = (ddspy_sample_container_t*) sample;
    //ddspy_serdata_ensure_sample(cserdata(dcmn));

    PyGILState_STATE state = PyGILState_Ensure();

    Py_INCREF(cserdata(dcmn)->sample);
    container->sample = cserdata(dcmn)->sample;

    PyGILState_Release(state);

    return false;
}

ddsi_serdata_t *serdata_to_typeless(const ddsi_serdata_t* dcmn)
{
    ddspy_serdata_t *d_tl = ddspy_serdata_new(dcmn->type, SDK_KEY, 16);

    d_tl->c_data.type = NULL; 
    d_tl->c_data.hash = dcmn->hash;
    d_tl->c_data.timestamp.v = INT64_MIN;
    d_tl->key = cserdata(dcmn)->key;
    d_tl->hash_populated = true;

    return (ddsi_serdata_t*) d_tl;
}

bool serdata_typeless_to_sample(
  const struct ddsi_sertype* type,
  const struct ddsi_serdata* dcmn, void* sample,
  void** bufptr, void* buflim)
{
    // TODO
    (void)type;
    (void)bufptr;
    (void)buflim;
    (void)sample;
    (void)dcmn;

    printf("Passing through typeless\n");

    return true;
}

void serdata_free(struct ddsi_serdata* dcmn)
{
    if (dcmn->kind == SDK_DATA && serdata(dcmn)->sample != NULL) {
        PyGILState_STATE state = PyGILState_Ensure();
        Py_XDECREF(serdata(dcmn)->sample);      
        PyGILState_Release(state);
    }

    free(serdata(dcmn)->data);
    free(dcmn);
}

size_t serdata_print(const struct ddsi_sertype* tpcmn, const struct ddsi_serdata* dcmn, char* buf, size_t bufsize)
{
    (void)tpcmn;

    //ddspy_serdata_ensure_sample(cserdata(dcmn));

    PyGILState_STATE state = PyGILState_Ensure();

    PyObject* repr = PyObject_Repr(cserdata(dcmn)->sample);
    PyObject* str = PyUnicode_AsEncodedString(repr, "utf-8", "~E~");
    const char *bytes = PyBytes_AS_STRING(str);

    strncpy(buf, bytes, bufsize);

    Py_XDECREF(repr);
    Py_XDECREF(str);

    PyGILState_Release(state);

    return 0;
}

void serdata_get_keyhash(const ddsi_serdata_t* d, struct ddsi_keyhash* buf, bool force_md5)
{
    if (force_md5 && !(((const ddspy_sertype_t*) d->type)->key_maxsize_bigger_16))
    {
        /// Since the maxkeysize < 16 the key is normally not md5 encoded
        /// We encode the key we already computed to avoid diving into python again
        ddsrt_md5_state_t md5st;
        ddsrt_md5_init(&md5st);
        ddsrt_md5_append(&md5st, cserdata(d)->key.value, 16);
        ddsrt_md5_finish(&md5st, buf->value);
    }
    else
    {
        memcpy(buf->value, cserdata(d)->key.value, 16);
    }
}

const struct ddsi_serdata_ops ddspy_serdata_ops = {
  &serdata_eqkey,
  &serdata_size,
  &serdata_from_ser,
  &serdata_from_ser_iov,
  &serdata_from_keyhash,
  &serdata_from_sample,
  &serdata_to_ser,
  &serdata_to_ser_ref,
  &serdata_to_ser_unref,
  &serdata_to_sample,
  &serdata_to_typeless,
  &serdata_typeless_to_sample,
  &serdata_free,
  &serdata_print,
  &serdata_get_keyhash
};


void sertype_free(struct ddsi_sertype* tpcmn)
{
    PyGILState_STATE state = PyGILState_Ensure();

    Py_XDECREF(((ddspy_sertype_t*) tpcmn)->my_py_type);
    Py_XDECREF(((ddspy_sertype_t*) tpcmn)->deserialize_attr);
    Py_XDECREF(((ddspy_sertype_t*) tpcmn)->serialize_attr);
    Py_XDECREF(((ddspy_sertype_t*) tpcmn)->key_calc_attr);
    Py_XDECREF(((ddspy_sertype_t*) tpcmn)->keyhash_calc_attr);

    PyGILState_Release(state);

    ddsi_sertype_fini(tpcmn);
}

void sertype_zero_samples(const struct ddsi_sertype* d, void* _sample, size_t size)
{
    (void) d;

    ddspy_sample_container_t *sample = (ddspy_sample_container_t*) _sample;

    PyGILState_STATE state = PyGILState_Ensure();

    for(size_t i = 0; i < size; ++i) {
        Py_XDECREF((sample+i)->sample);
        (sample+i)->sample = NULL;
    }

    PyGILState_Release(state);

    return;
}

void sertype_realloc_samples(void** ptrs, const struct ddsi_sertype* d, void* sample, size_t old, size_t new)
{
    ddspy_sample_container_t* newsamples = (ddspy_sample_container_t*) malloc(new * sizeof(ddspy_sample_container_t));

    if (sample == NULL) {
        // Initial alloc
        for(size_t i = 0; i < new; ++i)
            (newsamples+i)->sample = NULL;
        *ptrs = newsamples;
        return;
    }
    if (new > old) {
        memcpy(newsamples, sample, old * sizeof(ddspy_sample_container_t));

        for(size_t i = old; i < new; ++i)
            (newsamples+i)->sample = NULL;
    }
    else {
        ddspy_sample_container_t* newsamples = (ddspy_sample_container_t*) malloc(new * sizeof(ddspy_sample_container_t));
        memcpy(newsamples, sample, new * sizeof(ddspy_sample_container_t));
        sertype_zero_samples(d, ((ddspy_sample_container_t*) sample) + old, old - new);
    }

    free(sample);
    *ptrs = newsamples;
}

void sertype_free_samples(const struct ddsi_sertype* d, void** ptrs, size_t size, dds_free_op_t op)
{
    sertype_zero_samples(d, *ptrs, size);

    if (op & DDS_FREE_ALL_BIT) {
        free(*ptrs);
        *ptrs = NULL;
    }
}

bool sertype_equal(const ddsi_sertype_t* acmn, const ddsi_sertype_t* bcmn)
{
    /// Sertypes are equal if:
    ///    1: they point to the same point in memory (trivial)
    ///    1: they point to the same python object
    ///    2: the python objects they point to contain the same type info

    const ddspy_sertype_t *A = (const ddspy_sertype_t*) acmn;
    const ddspy_sertype_t *B = (const ddspy_sertype_t*) bcmn;

    if (A == B)
        return true;

    if (A->my_py_type == NULL || B->my_py_type == NULL) // should never be true
        return false;

    if (A->my_py_type == B->my_py_type)
        return true;

    // Expensive stuff coming up here
    PyGILState_STATE state = PyGILState_Ensure();
    int result = PyObject_RichCompareBool(A->my_py_type, B->my_py_type, Py_EQ);
    PyGILState_Release(state);

    return result == 1;
}

uint32_t sertype_hash(const struct ddsi_sertype* tpcmn)
{
  (void)tpcmn;
  return 0x0;
}


const struct ddsi_sertype_ops ddspy_sertype_ops = {
    ddsi_sertype_v0,
    NULL,

    &sertype_free,
    &sertype_zero_samples,
    &sertype_realloc_samples,
    &sertype_free_samples,
    &sertype_equal,
    &sertype_hash,

    /*typid_hash*/ NULL,
    /*serialized_size*/NULL,
    /*serialize*/NULL,
    /*deserialize*/NULL,
    /*assignable_from*/NULL
};


ddspy_sertype_t *ddspy_sertype_new(PyObject *pytype)
{
    ddspy_sertype_t *new = (ddspy_sertype_t*) malloc(sizeof(ddspy_sertype_t));

    PyObject* pyname = PyObject_GetAttrString(pytype, "typename");
    const char *name = PyUnicode_AsUTF8(pyname);

    PyObject* pykeyless = PyObject_GetAttrString(pytype, "keyless");
    bool keyless = pykeyless == Py_True;
    Py_DECREF(pykeyless);

    ddsi_sertype_init(
        &(new->my_c_type),
        name,
        &ddspy_sertype_ops,
        &ddspy_serdata_ops,
        keyless
    );
    Py_DECREF(pyname);

    Py_INCREF(pytype);
    new->my_py_type = pytype;
    new->deserialize_attr = PyObject_GetAttrString(pytype, "deserialize");
    new->serialize_attr = PyObject_GetAttrString(pytype, "serialize");

    if (!keyless)
    {
        new->key_calc_attr = PyObject_GetAttrString(pytype, "key");
        new->keyhash_calc_attr = PyObject_GetAttrString(pytype, "keyhash");

        PyObject* pykeysize = PyObject_GetAttrString(pytype, "key_max_size");
        long long keysize = PyLong_AsLongLong(pykeysize);
        Py_DECREF(pykeysize);
        new->key_maxsize_bigger_16 = keysize > 16;
    }

    return new;
}


/// Python BIND

static PyObject *
ddspy_topic_create(PyObject *self, PyObject *args)
{
    const char* name;
    PyObject* datatype;
    dds_entity_t participant;
    dds_entity_t sts;

    if (!PyArg_ParseTuple(args, "isO", &participant, &name, &datatype))
        return NULL;
    
    ddspy_sertype_t *sertype = ddspy_sertype_new(datatype);
    ddsi_sertype_t *rsertype = (ddsi_sertype_t*) sertype;
    sts = dds_create_topic_sertype(participant, name, (void**) &rsertype, NULL, NULL, NULL);

    return PyLong_FromLong((long)sts);
}

static PyObject *
ddspy_write(PyObject *self, PyObject *args)
{
    ddspy_sample_container_t container;
    dds_entity_t writer;
    dds_return_t sts;

    if (!PyArg_ParseTuple(args, "iO", &writer, &container.sample))
        return NULL;

    sts = dds_write(writer, &container);

    return PyLong_FromLong((long) sts);
}

static PyObject *
ddspy_read(PyObject *self, PyObject *args)
{
    dds_sample_info_t info;
    ddspy_sample_container_t container = {.sample=NULL};
    ddspy_sample_container_t* pcontainer = &container;
    dds_entity_t reader;
    dds_return_t sts;

    if (!PyArg_ParseTuple(args, "i", &reader))
        return NULL;

    sts = dds_read(reader, &pcontainer, &info, 1, 1);

    if (sts == 1) {  
        return pcontainer->sample;
    }

    return Py_None;
}


static PyObject *
ddspy_take(PyObject *self, PyObject *args)
{
    dds_sample_info_t info;
    ddspy_sample_container_t container = {.sample=NULL};
    ddspy_sample_container_t* pcontainer = &container;
    dds_entity_t reader;
    dds_return_t sts;

    if (!PyArg_ParseTuple(args, "i", &reader))
        return NULL;

    sts = dds_take(reader, &pcontainer, &info, 1, 1);

    if (sts == 1) {  
        return pcontainer->sample;
    }

    return Py_None;
}

char ddspy_docs[] = "DDSPY module";

PyMethodDef ddspy_funcs[] = {
	{	"ddspy_topic_create",
		(PyCFunction)ddspy_topic_create,
		METH_VARARGS,
		ddspy_docs},
    {	"ddspy_read",
		(PyCFunction)ddspy_read,
		METH_VARARGS,
		ddspy_docs},
    {	"ddspy_take",
		(PyCFunction)ddspy_take,
		METH_VARARGS,
		ddspy_docs},
    {	"ddspy_write",
		(PyCFunction)ddspy_write,
		METH_VARARGS,
		ddspy_docs},
	{	NULL}
};

char ddspymod_docs[] = "This is hello world module.";

PyModuleDef ddspy_mod = {
	PyModuleDef_HEAD_INIT,
	"ddspy",
	ddspymod_docs,
	-1,
	ddspy_funcs,
	NULL,
	NULL,
	NULL,
	NULL
};

PyMODINIT_FUNC PyInit_ddspy(void) {
	return PyModule_Create(&ddspy_mod);
}