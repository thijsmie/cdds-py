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

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include <inttypes.h>
#include "idl/string.h"
#include "idlpy/backendPyUtils.h"

#ifdef _WIN32
#pragma warning(disable : 4996)
#endif

/* Specify a list of all Python keywords */
static const char* py_keywords[] =
{
  /* QAC EXPECT 5007; Bypass qactools error */
  "False", "None", "True", "__peg_parser__", "and", "as",
  "assert", "async", "await", "break", "class", "continue",
  "def", "del", "elif", "else", "except", "finally", "for",
  "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
  "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"
};

char*
get_py_name(const char* name)
{
  char* pyName;
  size_t i;

  /* search through the Python keyword list */
  for (i = 0; i < sizeof(py_keywords) / sizeof(char*); i++) {
    if (strcmp(py_keywords[i], name) == 0) {
      /* If a keyword matches the specified identifier, prepend py_ */
      /* QAC EXPECT 5007; will not use wrapper */
      size_t pyNameLen = strlen(name) + 5 + 1;
      pyName = malloc(pyNameLen);
      snprintf(pyName, pyNameLen, "py_%s", name);
      return pyName;
    }
  }
  /* No match with a keyword is found, thus return the identifier itself */
  pyName = idl_strdup(name);
  return pyName;
}

static char *
get_py_base_type(const idl_node_t *node)
{
  static const idl_mask_t mask = (IDL_BASE_TYPE|(IDL_BASE_TYPE-1));

  switch (idl_mask(node) & mask)
  {
  case IDL_CHAR:
    return idl_strdup("char");
  case IDL_WCHAR:
    return idl_strdup("wchar");
  case IDL_BOOL:
    return idl_strdup("bool");
  case IDL_INT8:
    return idl_strdup("int8");
  case IDL_UINT8:
  case IDL_OCTET:
    return idl_strdup("uint8");
  case IDL_INT16:
    return idl_strdup("int16");
  case IDL_UINT16:
    return idl_strdup("uint16");
  case IDL_INT32:
    return idl_strdup("int32");
  case IDL_UINT32:
    return idl_strdup("uint32");
  case IDL_INT64:
    return idl_strdup("int64");
  case IDL_UINT64:
    return idl_strdup("uint64");
  case IDL_FLOAT:
    return idl_strdup("float32");
  case IDL_DOUBLE:
    return idl_strdup("float64");
  case IDL_LDOUBLE:
    /// Python has no way to represent this type properly
    assert(0);
    break;
  default:
    assert(0);
    break;
  }
  return NULL;
}

static char *
get_py_templ_type(const idl_node_t *node)
{
  char *pyType = NULL;

  switch (idl_mask(node) & IDL_TEMPL_TYPE_MASK)
  {
  case IDL_SEQUENCE:
    {
      uint64_t bound = ((const idl_sequence_t*)node)->maximum;
      char* vector_element = get_py_type(((const idl_sequence_t*)node)->type_spec);
      if (bound)
        idl_asprintf(&pyType, PY_BOUNDED_SEQUENCE_TEMPLATE(vector_element, bound));
      else
        idl_asprintf(&pyType, PY_SEQUENCE_TEMPLATE(vector_element));
      free(vector_element);
    }
    break;
  case IDL_STRING:
    {
      uint64_t bound = ((const idl_string_t*)node)->maximum;
      if (bound)
        idl_asprintf(&pyType, PY_BOUNDED_STRING_TEMPLATE(bound));
      else
        idl_asprintf(&pyType, PY_STRING_TEMPLATE());
    }
    break;
  case IDL_WSTRING:
    //currently not supported
    assert(0);
    break;
  case IDL_FIXED_PT:
    //currently not supported
    assert(0);
    break;
  default:
    assert(0);
    break;
  }

  return pyType;
}

char *
get_py_type(const idl_node_t *node)
{
  assert(idl_mask(node) & (IDL_BASE_TYPE|IDL_TEMPL_TYPE|IDL_CONSTR_TYPE|IDL_TYPEDEF));
  if (idl_is_base_type(node))
    return get_py_base_type(node);
  else if (idl_is_templ_type(node))
    return get_py_templ_type(node);
  else
    return get_py_fully_scoped_name(node);
}

char *
get_py_fully_scoped_name(const idl_node_t *node)
{
  uint32_t nr_scopes = 0;
  size_t scoped_enumerator_len = 0;
  char *scoped_enumerator;
  char **scope_names;
  const idl_node_t *current_node = node;
  idl_mask_t scope_type;

  while (current_node) {
    ++nr_scopes;
    current_node = current_node->parent;
  }
  scope_names = malloc(sizeof(char *) * nr_scopes);
  current_node = node;
  for (uint32_t i = 0; i < nr_scopes; ++i)
  {
    scope_type = idl_mask(current_node) & (IDL_MODULE | IDL_ENUMERATOR | IDL_ENUM | IDL_STRUCT | IDL_UNION | IDL_TYPEDEF);
    assert(scope_type);
    switch (scope_type)
    {
    case IDL_ENUMERATOR:
      scope_names[i] = get_py_name(idl_identifier(current_node));
      break;
    case IDL_ENUM:
      scope_names[i] = get_py_name(idl_identifier(current_node));
      break;
    case IDL_MODULE:
      scope_names[i] = get_py_name(idl_identifier(current_node));
      break;
    case IDL_STRUCT:
      scope_names[i] = get_py_name(idl_identifier(current_node));
      break;
    case IDL_UNION:
      scope_names[i] = get_py_name(idl_identifier(current_node));
      break;
    case IDL_TYPEDEF:
      scope_names[i] = get_py_name(idl_identifier(((const idl_typedef_t *)current_node)->declarators));
      break;
    }
    scoped_enumerator_len += (strlen(scope_names[i]) + 1); /* scope + "." */
    current_node = current_node->parent;
  }
  scoped_enumerator = malloc(++scoped_enumerator_len); /* Add one for '\0' */
  scoped_enumerator[0] = '\0';
  while(nr_scopes)
  {
    strncat(scoped_enumerator, ".", scoped_enumerator_len);
    strncat(scoped_enumerator, scope_names[--nr_scopes], scoped_enumerator_len);
    free(scope_names[nr_scopes]);
  }
  free(scope_names);
  return scoped_enumerator;
}

char *
get_default_value(idl_backend_ctx ctx, const idl_node_t *node)
{
  static const idl_mask_t mask = (IDL_BASE_TYPE|(IDL_BASE_TYPE-1));
  (void)ctx;

  if (idl_is_enum(node))
    return get_py_fully_scoped_name((idl_node_t*)((idl_enum_t*)node)->enumerators);

  switch (idl_mask(node) & mask)
  {
  case IDL_BOOL:
    return idl_strdup("False");
  case IDL_CHAR:
  case IDL_WCHAR:
  case IDL_OCTET:
    return idl_strdup("0");
  case IDL_FLOAT:
    return idl_strdup("0.0");
  case IDL_DOUBLE:
  case IDL_LDOUBLE:
    return idl_strdup("0.0");
  case IDL_INT8:
  case IDL_UINT8:
  case IDL_INT16:
  case IDL_UINT16:
  case IDL_INT32:
  case IDL_UINT32:
  case IDL_INT64:
  case IDL_UINT64:
    return idl_strdup("0");
  default:
    return NULL;
  }
}

static char *
get_py_base_type_const_value(const idl_constval_t *constval)
{
  int cnt = -1;
  char *str = NULL;
  static const idl_mask_t mask = (IDL_BASE_TYPE_MASK|(IDL_BASE_TYPE_MASK-1));

  switch (idl_mask(&constval->node) & mask)
  {
  case IDL_BOOL:
    return idl_strdup(constval->value.bln ? "true" : "false");
  case IDL_INT8:
    cnt = idl_asprintf(&str, "%" PRId8, constval->value.int8);
    break;
  case IDL_UINT8:
  case IDL_OCTET:
    cnt = idl_asprintf(&str, "%" PRIu8, constval->value.uint8);
    break;
  case IDL_INT16:
  case IDL_SHORT:
    cnt = idl_asprintf(&str, "%" PRId16, constval->value.int16);
    break;
  case IDL_UINT16:
  case IDL_USHORT:
    cnt = idl_asprintf(&str, "%" PRIu16, constval->value.uint16);
    break;
  case IDL_INT32:
  case IDL_LONG:
    cnt = idl_asprintf(&str, "%" PRId32, constval->value.int32);
    break;
  case IDL_UINT32:
  case IDL_ULONG:
    cnt = idl_asprintf(&str, "%" PRIu32, constval->value.uint32);
    break;
  case IDL_INT64:
  case IDL_LLONG:
    cnt = idl_asprintf(&str, "%" PRId64, constval->value.int64);
    break;
  case IDL_UINT64:
  case IDL_ULLONG:
    cnt = idl_asprintf(&str, "%" PRIu64, constval->value.uint64);
    break;
  case IDL_FLOAT:
    cnt = idl_asprintf(&str, "%.6f", constval->value.flt);
    break;
  case IDL_DOUBLE:
    cnt = idl_asprintf(&str, "%f", constval->value.dbl);
    break;
  case IDL_LDOUBLE:
    cnt = idl_asprintf(&str, "%Lf", constval->value.ldbl);
    break;
  case IDL_CHAR:
    cnt = idl_asprintf(&str, "\'%c\'", constval->value.chr);
    break;
  case IDL_STRING:
    cnt = idl_asprintf(&str, "\"%s\"", constval->value.str);
    break;
  default:
    assert(0);
    break;
  }

  return cnt >= 0 ? str : NULL;
}

static char *
get_py_templ_type_const_value(const idl_constval_t *constval)
{
  char *str;
  size_t len;

  if (!idl_is_masked(constval, IDL_STRING))
    return NULL;
  assert(constval->value.str);
  len = strlen(constval->value.str);
  if (!(str = malloc(len + 2 /* quotes */ + 1)))
    return NULL;
  str[0] = '"';
  memcpy(str + 1, constval->value.str, len);
  str[1 + len] = '"';
  str[1 + len + 1] = '\0';
  return str;
}

char *
get_py_const_value(const idl_constval_t *constval)
{
  static const idl_mask_t mask = IDL_BASE_TYPE | IDL_TEMPL_TYPE | IDL_ENUMERATOR;

  switch (idl_mask(&constval->node) & mask) {
  case IDL_BASE_TYPE:
    return get_py_base_type_const_value(constval);
  case IDL_TEMPL_TYPE:
    return get_py_templ_type_const_value(constval);
  case IDL_ENUMERATOR:
    return get_py_fully_scoped_name((const idl_node_t *)constval);
  default:
    assert(0);
    break;
  }
  return NULL;
}

void
print_py_imports(idl_backend_ctx ctx)
{
  idl_file_out_printf(ctx, "from enum import Enum, auto\n");
  idl_file_out_printf(ctx, "from typing import List, Annotated\n");
  idl_file_out_printf(ctx, "from pycdr import cdr\n");
  idl_file_out_printf(ctx, "from pycdr.types import union, int8, int16, int32, int64, char, wchar,\\\n");
  idl_file_out_printf(ctx, "\t\tuint8, uint16, uint32, uint64, float32, float64\n\n\n");
}