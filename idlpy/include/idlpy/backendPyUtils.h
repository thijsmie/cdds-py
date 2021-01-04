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
#include <inttypes.h>
#include "idlpy/backend.h"

#define PY_SEQUENCE_TEMPLATE(type)                 "List[%s]", type
#define PY_BOUNDED_SEQUENCE_TEMPLATE(type, bound)  "Annotated[List[%s], MaxLen(%s)]", type, bound
#define PY_ARRAY_TEMPLATE(element, const_expr)     "Annotated[List[%s], Len[%s]]", element, const_expr
#define PY_STRING_TEMPLATE()                       "str"
#define PY_BOUNDED_STRING_TEMPLATE(bound)          "Annotated[str, MaxLen[%s]]", bound

#ifdef WIN32
#include <direct.h>
#define mkdir(dir, mode) _mkdir(dir)
#else
#include <sys/stat.h>
#endif

char*
get_py_name(const char* name);

char *
get_py_type(const idl_node_t *node);

char *
get_py_fully_scoped_name(const idl_node_t *node);

char *
get_default_value(idl_backend_ctx ctx, const idl_node_t *node);

char *
get_py_const_value(const idl_constval_t *literal);

void
print_py_imports(idl_backend_ctx ctx);

typedef struct idl_backend_py_ctx_s {
    const char *basedir;
    const char *target_file;
} *idl_backend_py_ctx;