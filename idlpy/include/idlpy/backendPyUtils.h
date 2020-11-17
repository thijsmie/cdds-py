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

// replace the definitions below (PY_...) with your own custom classes and includes.

#define PY_SEQUENCE_TEMPLATE(type)                 "c_list[%s]", type

// default (C++ STL) container definitions
// bounded sequences require a template class taking a single typename and a single size
// E.G. custom_bounded_vector<custom_class,255>
//#define PY_BOUNDED_SEQUENCE_TEMPLATE(type, bound)  "non_std::vector<%s, %" PRIu64 ">", type, bound
#define PY_BOUNDED_SEQUENCE_TEMPLATE(type, bound)  "c_list[%s]", type

// array templates
// arrays require a template class taking a with a single typename and a single size
// E.G. custom_array<custom_class,16>
#define PY_ARRAY_TEMPLATE(element, const_expr)     "c_list[%s, %s]", element, const_expr

// string templates
// unbounded strings require just a class name
// E.G. std::string
#define PY_STRING_TEMPLATE()                       "c_char_p"

// bounded strings require a template class with a single size
// E.G. custom_bounded_string<127>
//#define PY_BOUNDED_STRING_TEMPLATE(bound)          "non_std::string<%" PRIu64 ">", bound
#define PY_BOUNDED_STRING_TEMPLATE(bound)          "c_char_p[%s]", bound

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

char *
get_py_literal_value(const idl_literal_t *literal);

