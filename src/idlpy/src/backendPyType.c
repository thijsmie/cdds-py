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
#include <assert.h>
#include <stdlib.h>
#include <limits.h>

#include "idlpy/backendPyUtils.h"
#include "idlpy/backendPyType.h"
#include "idlpy/backend.h"
#include "idl/string.h"

typedef struct py_member_state_s
{
  const idl_node_t *member_type_node;
  const idl_declarator_t *declarator_node;
  char *name;
  char *type_name;
} py_member_state;

typedef struct py_struct_context_s
{
  py_member_state *members;
  uint32_t member_count;
  char *name;
  char *base_type;
} py_struct_context;

static idl_retcode_t
py_scope_walk(idl_backend_ctx ctx, const idl_node_t *node);

static idl_retcode_t
count_declarators(idl_backend_ctx ctx, const idl_node_t *node)
{
  uint32_t *nr_members = (uint32_t *) idl_get_custom_context(ctx);
  (void)node;
  ++(*nr_members);
  return IDL_RETCODE_OK;
}

static idl_retcode_t
count_members(idl_backend_ctx ctx, const idl_node_t *node)
{
  const idl_member_t *member = (const idl_member_t *) node;
  const idl_node_t *declarators = (const idl_node_t *) member->declarators;
  return idl_walk_node_list(ctx, declarators, count_declarators, IDL_DECLARATOR);
}

static char *
get_py_declarator_array_expr(idl_backend_ctx ctx, const idl_node_t *node, const char *member_type)
{
  idl_node_t *next_const_expr = node->next;
  char *element_expr, *const_expr, *array_expr = NULL;

  if (next_const_expr) {
    element_expr = get_py_declarator_array_expr(ctx, next_const_expr, member_type);
  } else {
    element_expr = idl_strdup(member_type);
  }
  const_expr = get_py_const_value((const idl_constval_t *)node);
  idl_asprintf(&array_expr, PY_ARRAY_TEMPLATE(element_expr, const_expr));
  free(const_expr);
  free(element_expr);
  return array_expr;
}

static idl_retcode_t
get_py_declarator_data(idl_backend_ctx ctx, const idl_node_t *node)
{
  py_struct_context *struct_ctx = (py_struct_context *) idl_get_custom_context(ctx);
  py_member_state *member_data = &struct_ctx->members[struct_ctx->member_count];
  const idl_declarator_t *declarator = (const idl_declarator_t *) node;

  member_data->member_type_node = ((const idl_member_t *) node->parent)->type_spec;
  member_data->declarator_node = declarator;
  member_data->name = get_py_name(idl_identifier(declarator));
  member_data->type_name = get_py_type(member_data->member_type_node);
  /* Check if the declarator contains also an array expression... */
  if (idl_declarator_is_array(declarator))
  {
    char *array_expr = get_py_declarator_array_expr(ctx, declarator->const_expr, member_data->type_name);
    free(member_data->type_name);
    member_data->type_name = array_expr;
  }
  ++(struct_ctx->member_count);
  return IDL_RETCODE_OK;
}

static idl_retcode_t
get_py_member_data(idl_backend_ctx ctx, const idl_node_t *node)
{
  const idl_member_t *member = (const idl_member_t *) node;
  const idl_node_t *declarators = (const idl_node_t *) member->declarators;
  return idl_walk_node_list(ctx, declarators, get_py_declarator_data, IDL_DECLARATOR);
}

static void
struct_generate_variables(idl_backend_ctx ctx)
{
  py_struct_context *struct_ctx = (py_struct_context *) idl_get_custom_context(ctx);

  /* Declare all the member variables. */
  idl_indent_incr(ctx);
  for (uint32_t i = 0; i < struct_ctx->member_count; ++i)
  {
    idl_file_out_printf(ctx, "%s: %s\n",
        struct_ctx->members[i].name,
        struct_ctx->members[i].type_name);
  }
  idl_indent_decr(ctx);
}

static idl_retcode_t
struct_generate_body(idl_backend_ctx ctx, const idl_struct_t *struct_node)
{
  void* out_ctx = idl_get_custom_context(ctx);
  idl_reset_custom_context(ctx);

  idl_retcode_t result = IDL_RETCODE_OK;

  uint32_t nr_members = 0;
  py_struct_context struct_ctx;
  const idl_node_t *members = (const idl_node_t *) struct_node->members;
  result = idl_set_custom_context(ctx, &nr_members);
  if (result) return result;
  idl_walk_node_list(ctx, members, count_members, IDL_MEMBER);
  idl_reset_custom_context(ctx);

  struct_ctx.members = malloc(sizeof(py_member_state) * nr_members);
  struct_ctx.member_count = 0;
  struct_ctx.name = get_py_name(idl_identifier(struct_node));

  if (struct_node->inherit_spec)
  {
    const idl_node_t *base_node = (const idl_node_t *) struct_node->inherit_spec->base;
    struct_ctx.base_type = get_py_fully_scoped_name(base_node);
  }
  else
  {
    struct_ctx.base_type = NULL;
  }
  
  result = idl_set_custom_context(ctx, &struct_ctx);
  if (result) return result;
  idl_walk_node_list(ctx, members, get_py_member_data, IDL_MEMBER);

  /* Create class declaration. */
  if (struct_ctx.base_type) {
    idl_file_out_printf(ctx, "\n@cdr\n");
    idl_file_out_printf(ctx, "class %s(%s):\n", struct_ctx.name, struct_ctx.base_type);
  } else {
    idl_file_out_printf(ctx, "\n@cdr\n");
    idl_file_out_printf(ctx, "class %s:\n", struct_ctx.name);
  }

  /* Create struct variables. */
  struct_generate_variables(ctx);
  idl_file_out_printf(ctx, "\n");

  idl_reset_custom_context(ctx);
  for (uint32_t i = 0; i < nr_members; ++i)
  {
    free(struct_ctx.members[i].name);
    free(struct_ctx.members[i].type_name);
  }
  free(struct_ctx.members);
  if (struct_ctx.base_type) free(struct_ctx.base_type);
  free(struct_ctx.name);
  idl_set_custom_context(ctx, out_ctx);

  return result;
}

typedef struct py_case_state_s
{
  const idl_node_t *typespec_node;
  const idl_declarator_t *declarator_node;
  char *name;
  char *type_name;
  uint32_t label_count;
  char **labels;
} py_case_state;

typedef struct py_union_context_s
{
  py_case_state *cases;
  uint32_t case_count;
  uint64_t total_label_count, nr_unused_discr_values;
  const idl_node_t *discr_node;
  char *discr_type;
  const char *name;
  const py_case_state *default_case;
  char *default_label;
  bool has_impl_default;
} py_union_context;

static idl_retcode_t
count_labels(idl_backend_ctx ctx, const idl_node_t *node)
{
  uint32_t *nr_labels = (uint32_t *) idl_get_custom_context(ctx);
  (void)node;
  ++(*nr_labels);
  return IDL_RETCODE_OK;
}

static idl_retcode_t
count_cases(idl_backend_ctx ctx, const idl_node_t *node)
{
  uint32_t *nr_cases = (uint32_t *) idl_get_custom_context(ctx);
  (void)node;
  ++(*nr_cases);
  return IDL_RETCODE_OK;
}

static char *
get_label_value(const idl_case_label_t *label)
{
  char *label_value;

  if (idl_mask(label->const_expr) & IDL_ENUMERATOR) {
    label_value = get_py_fully_scoped_name(label->const_expr);
  } else {
    label_value = get_py_const_value((const idl_constval_t *) label->const_expr);
  }

  return label_value;
}

static idl_retcode_t
get_py_labels(idl_backend_ctx ctx, const idl_node_t *node)
{
  py_union_context *union_ctx = (py_union_context *) idl_get_custom_context(ctx);
  const idl_case_label_t *label = (const idl_case_label_t *) node;
  py_case_state *case_data = &union_ctx->cases[union_ctx->case_count];
  /* Check if there is a label: if not it represents the default case. */
  if (label->const_expr) {
    case_data->labels[case_data->label_count] = get_label_value(label);
  } else {
    /* Assert that there can only be one default case */
    assert(union_ctx->default_case == NULL);
    union_ctx->default_case = case_data;
    case_data->labels[case_data->label_count] = NULL;
  }
  ++(case_data->label_count);
  return IDL_RETCODE_OK;
}

static idl_retcode_t
get_py_case_data(idl_backend_ctx ctx, const idl_node_t *node)
{
  idl_retcode_t result;
  py_union_context *union_ctx = (py_union_context *) idl_get_custom_context(ctx);
  py_case_state *case_data = &union_ctx->cases[union_ctx->case_count];
  const idl_case_t *case_node = (const idl_case_t *) node;
  const idl_node_t *case_labels = (const idl_node_t *) case_node->case_labels;
  uint32_t label_count = 0;

  idl_reset_custom_context(ctx);
  result = idl_set_custom_context(ctx, &label_count);
  if (result) return result;
  idl_walk_node_list(ctx, case_labels, count_labels, IDL_CASE_LABEL);
  union_ctx->total_label_count += label_count;
  idl_reset_custom_context(ctx);
  result = idl_set_custom_context(ctx, union_ctx);
  if (result) return result;

  case_data->typespec_node = case_node->type_spec;
  case_data->declarator_node = case_node->declarator;
  case_data->name = get_py_name(idl_identifier(case_node->declarator));
  case_data->label_count = 0;
  if (label_count > 0) {
    case_data->labels = malloc(sizeof(char *) * label_count);
  } else {
    case_data->labels = NULL;
  }
  case_data->type_name = get_py_type(case_node->type_spec);
  /* Check if the declarator contains also an array expression... */
  if (idl_declarator_is_array(case_data->declarator_node))
  {
    char *array_expr = get_py_declarator_array_expr(
        ctx, case_data->declarator_node->const_expr, case_data->type_name);
    free(case_data->type_name);
    case_data->type_name = array_expr;
  }
  idl_walk_node_list(ctx, case_labels, get_py_labels, IDL_CASE_LABEL);

  ++(union_ctx->case_count);
  return IDL_RETCODE_OK;
}
static uint64_t
get_potential_nr_discr_values(const idl_union_t *union_node)
{
  uint64_t nr_discr_values = 0;
  const idl_type_spec_t *node = union_node->switch_type_spec ? union_node->switch_type_spec->type_spec : NULL;

  switch (idl_mask(node) & (IDL_BASE_TYPE | IDL_CONSTR_TYPE))
  {
  case IDL_BASE_TYPE:
    switch (idl_mask(node) & IDL_BASE_TYPE_MASK)
    {
    case IDL_INTEGER_TYPE:
      switch(idl_mask(node) & IDL_INTEGER_MASK_IGNORE_SIGN)
      {
      case IDL_INT8:
        nr_discr_values = UINT8_MAX;
        break;
      case IDL_INT16:
      case IDL_SHORT:
        nr_discr_values = UINT16_MAX;
        break;
      case IDL_INT32:
      case IDL_LONG:
        nr_discr_values = UINT32_MAX;
        break;
      case IDL_INT64:
      case IDL_LLONG:
        nr_discr_values = UINT64_MAX;
        break;
      default:
        assert(0);
        break;
      }
      break;
    default:
      switch(idl_mask(node) & IDL_BASE_OTHERS_MASK)
      {
      case IDL_CHAR:
      case IDL_OCTET:
        nr_discr_values = UINT8_MAX;
        break;
      case IDL_WCHAR:
        nr_discr_values = UINT16_MAX;
        break;
      case IDL_BOOL:
        nr_discr_values = 2;
        break;
      default:
        assert(0);
        break;
      }
      break;
    }
    break;
  case IDL_CONSTR_TYPE:
    switch (idl_mask(node) & IDL_ENUM)
    {
    case IDL_ENUM:
    {
      /* Pick the first of the available enumerators. */
      const idl_enum_t *enumeration = (const idl_enum_t *) node;
      const idl_enumerator_t* enumerator = enumeration->enumerators;
      nr_discr_values = 0;
      while(enumerator)
      {
        ++nr_discr_values;
        enumerator = (const idl_enumerator_t*)enumerator->node.next;
      }
      break;
    }
    default:
      assert(0);
      break;
    }
    break;
  default:
    assert(0);
    break;
  }
  return nr_discr_values;
}
static idl_constval_t
get_min_value(const idl_node_t *node)
{
  idl_constval_t result;
  static const idl_mask_t mask = (IDL_BASE_TYPE|(IDL_BASE_TYPE-1));

  result.node = *node;
  result.node.symbol.mask &= mask;
  switch (idl_mask(node) & mask)
  {
  case IDL_BOOL:
    result.value.bln = false;
    break;
  case IDL_CHAR:
    result.value.chr = 0;
    break;
  case IDL_INT8:
    result.value.int8 = INT8_MIN;
    break;
  case IDL_UINT8:
  case IDL_OCTET:
    result.value.uint8 = 0;
    break;
  case IDL_INT16:
  case IDL_SHORT:
    result.value.int16 = INT16_MIN;
    break;
  case IDL_UINT16:
  case IDL_USHORT:
    result.value.uint16 = 0;
    break;
  case IDL_INT32:
  case IDL_LONG:
    result.value.int32 = INT32_MIN;
    break;
  case IDL_UINT32:
  case IDL_ULONG:
    result.value.uint32 = 0;
    break;
  case IDL_INT64:
  case IDL_LLONG:
    result.value.int64 = INT64_MIN;
    break;
  case IDL_UINT64:
  case IDL_ULLONG:
    result.value.uint64 = 0ULL;
    break;
  default:
    assert(0);
    break;
  }
  result.node.symbol.mask |= IDL_CONST;
  return result;
}

static void *
enumerator_incr_value(void *val)
{
  const idl_enumerator_t *enum_val = (const idl_enumerator_t *) val;
  return enum_val->node.next;
}

static void *
constval_incr_value(void *val)
{
  idl_constval_t *cv = (idl_constval_t *)val;
  static const idl_mask_t mask = (IDL_BASE_TYPE|(IDL_BASE_TYPE-1));

  switch (idl_mask(&cv->node) & mask)
  {
  case IDL_BOOL:
    cv->value.bln = true;
    break;
  case IDL_INT8:
    cv->value.int8++;
    break;
  case IDL_UINT8:
    cv->value.uint8++;
    break;
  case IDL_INT16:
    cv->value.int16++;
    break;
  case IDL_UINT16:
    cv->value.uint16++;
    break;
  case IDL_INT32:
    cv->value.int32++;
    break;
  case IDL_UINT32:
    cv->value.uint32++;
    break;
  case IDL_INT64:
    cv->value.int64++;
    break;
  case IDL_UINT64:
    cv->value.uint64++;
    break;
  default:
    assert(0);
    break;
  }
  return cv;
}

typedef enum { IDL_LT, IDL_EQ, IDL_GT} idl_equality_t;
typedef idl_equality_t (*idl_comparison_fn) (const void *element1, const void *element2);
typedef void *(*idl_incr_element_fn) (void *element1);

static idl_equality_t
compare_enum_elements(const void *element1, const void *element2)
{
  const idl_enumerator_t *enumerator1 = (const idl_enumerator_t *) element1;
  const idl_enumerator_t *enumerator2 = (const idl_enumerator_t *) element2;
  idl_equality_t result = IDL_EQ;

  if (enumerator1->value < enumerator2->value) result = IDL_LT;
  if (enumerator1->value > enumerator2->value) result = IDL_GT;
  return result;
}

static idl_equality_t
compare_const_elements(const void *element1, const void *element2)
{
#define EQ(a,b) ((a<b) ? IDL_LT : ((a>b) ? IDL_GT : IDL_EQ))
  const idl_constval_t *cv1 = (const idl_constval_t *) element1;
  const idl_constval_t *cv2 = (const idl_constval_t *) element2;
  static const idl_mask_t mask = IDL_BASE_TYPE|(IDL_BASE_TYPE-1);

  assert((idl_mask(&cv1->node) & mask) == (idl_mask(&cv2->node) & mask));
  switch (idl_mask(&cv1->node) & mask)
  {
  case IDL_BOOL:
    return EQ(cv1->value.bln, cv2->value.bln);
  case IDL_INT8:
    return EQ(cv1->value.int8, cv2->value.int8);
  case IDL_UINT8:
  case IDL_OCTET:
    return EQ(cv1->value.uint8, cv2->value.uint8);
  case IDL_INT16:
  case IDL_SHORT:
    return EQ(cv1->value.int16, cv2->value.int16);
  case IDL_UINT16:
  case IDL_USHORT:
    return EQ(cv1->value.uint16, cv2->value.uint16);
  case IDL_INT32:
  case IDL_LONG:
    return EQ(cv1->value.int32, cv2->value.int32);
  case IDL_UINT32:
  case IDL_ULONG:
    return EQ(cv1->value.uint32, cv2->value.uint32);
  case IDL_INT64:
  case IDL_LLONG:
    return EQ(cv1->value.int64, cv2->value.int64);
  case IDL_UINT64:
  case IDL_ULLONG:
    return EQ(cv1->value.uint64, cv2->value.uint64);
  default:
    assert(0);
    break;
  }
  return IDL_EQ;
#undef EQ
}

static void
swap(void **element1, void **element2)
{
  void *tmp = *element1;
  *element1 = *element2;
  *element2 = tmp;
}

static uint64_t
manage_pivot (void **array, uint64_t low, uint64_t high, idl_comparison_fn compare_elements)
{
  uint64_t i = low;
  void *pivot = array[high];

  for (uint64_t j = low; j <= high- 1; j++)
  {
    if (compare_elements(&array[j], &pivot) == IDL_LT)
    {
      swap(&array[i++], &array[j]);
    }
  }
  swap(&array[i + 1], &array[high]);
  return (i + 1);
}

static void quick_sort(void **array, uint64_t low, uint64_t high, idl_comparison_fn compare_elements)
{
  uint64_t pivot_index;

  if (low < high)
  {
    pivot_index = manage_pivot(array, low, high, compare_elements);
    quick_sort(array, low, pivot_index - 1, compare_elements);
    quick_sort(array, pivot_index + 1, high, compare_elements);
  }
}

static char *
get_first_unused_discr_value(
    void **array,
    void *min_value,
    void *max_value,
    idl_comparison_fn compare_elements,
    idl_incr_element_fn incr_element)
{

  uint32_t i = 0;
  do
  {
    if (compare_elements(min_value, array[i]) == IDL_LT)
    {
      return get_py_const_value(min_value);
    }
    min_value = incr_element(min_value);
    if (array[i] != max_value) ++i;
  } while (compare_elements(min_value, array[i]) != IDL_GT);
  return get_py_const_value(min_value);
}

static char *
get_default_discr_value(idl_backend_ctx ctx, const idl_union_t *union_node)
{
  py_union_context *union_ctx = (py_union_context *) idl_get_custom_context(ctx);
  char *def_value = NULL;
  union_ctx->nr_unused_discr_values =
      get_potential_nr_discr_values(union_node) - union_ctx->total_label_count;
  idl_constval_t min_const_value;
  void *min_value;
  idl_comparison_fn compare_elements;
  idl_incr_element_fn incr_element;

  if (union_ctx->nr_unused_discr_values) {
    /* find the smallest available unused discr_value. */
    void **all_labels = malloc(sizeof(void *) * (size_t)union_ctx->total_label_count);
    uint32_t i = 0;
    const idl_case_t *case_data = union_node->cases;
    while (case_data)
    {
      const idl_case_label_t *label = case_data->case_labels;
      while (label)
      {
        all_labels[i++] = label->const_expr;
        label = (const idl_case_label_t *) label->node.next;
      }
      case_data = (const idl_case_t *) case_data->node.next;
    }
    if (idl_mask(union_node->switch_type_spec->type_spec) & IDL_ENUM) {
      compare_elements = compare_enum_elements;
      incr_element = enumerator_incr_value;
      min_value = ((const idl_enum_t *)union_ctx->discr_node)->enumerators;
    } else {
      compare_elements = compare_const_elements;
      incr_element = constval_incr_value;
      min_const_value = get_min_value((idl_node_t*)union_node->switch_type_spec->type_spec);
      min_value = &min_const_value;
    }
    quick_sort(all_labels, 0, union_ctx->total_label_count - 1, compare_elements);
    def_value = get_first_unused_discr_value(
        all_labels,
        min_value,
        all_labels[union_ctx->total_label_count - 1],
        compare_elements,
        incr_element);
    if (!union_ctx->default_case) union_ctx->has_impl_default = true;
    free(all_labels);
  } else {
    /* Pick the first available literal value from the first available case. */
    const idl_const_expr_t *const_expr = union_node->cases->case_labels->const_expr;
    def_value = get_py_const_value((const idl_constval_t *) const_expr);
  }

  return def_value;
}

static void
union_generate_attributes(idl_backend_ctx ctx)
{
  py_union_context *union_ctx = (py_union_context *) idl_get_custom_context(ctx);

  idl_indent_incr(ctx);

  /* Declare a union attribute comprising of all the branch types. */

  for (uint32_t i = 0; i < union_ctx->case_count; ++i) {
    idl_file_out_printf(
        ctx,
        "%s: %s = case(",
        union_ctx->cases[i].name,
        union_ctx->cases[i].type_name);

    for (int32_t j = 0; j < union_ctx->cases[i].label_count; ++j) {
      idl_file_out_printf_no_indent(ctx,
        "%s%s",
        union_ctx->cases[i].labels[j],
        (j ==  (union_ctx->cases[i].label_count - 1)) ? "" : ", "
      );
    }

    idl_file_out_printf_no_indent(ctx, ")\n");
  }

  idl_file_out_printf(
    ctx,
    "%s: %s = default(%s)",
    union_ctx->default_case->name,
    union_ctx->default_case->type_name,
    union_ctx->default_label
  );

  idl_file_out_printf_no_indent(ctx, ")\n");
  idl_indent_decr(ctx);
}

static void
union_generate_constructor(idl_backend_ctx ctx)
{
  py_union_context *union_ctx = (py_union_context *) idl_get_custom_context(ctx);

  idl_indent_incr(ctx);

  /* Start building default (empty) constructor. */
  idl_file_out_printf(ctx, "def __init__(self):\n");
  idl_indent_incr(ctx);
  idl_file_out_printf(ctx, "self.discriminator = %s\n", union_ctx->default_label);
  idl_file_out_printf(ctx, "self.value = None\n");
  idl_indent_decr(ctx);
  idl_indent_decr(ctx);
}

static idl_retcode_t
union_generate_body(idl_backend_ctx ctx, const idl_union_t *union_node)
{
  idl_retcode_t result = IDL_RETCODE_OK;
  char *pyName = get_py_name(idl_identifier(union_node));
  void *out_ctx = idl_get_custom_context(ctx);
  idl_reset_custom_context(ctx);

  uint32_t nr_cases = 0;
  const idl_node_t *cases = (const idl_node_t *) union_node->cases;
  py_union_context union_ctx;
  result = idl_set_custom_context(ctx, &nr_cases);
  if (result) return result;
  idl_walk_node_list(ctx, cases, count_cases, IDL_CASE);
  idl_reset_custom_context(ctx);

  union_ctx.cases = malloc(sizeof(py_case_state) * nr_cases);
  union_ctx.case_count = 0;
  union_ctx.discr_node = (idl_node_t*)union_node->switch_type_spec->type_spec;
  union_ctx.discr_type = get_py_type((idl_node_t*)union_node->switch_type_spec->type_spec);
  union_ctx.name = pyName;
  union_ctx.default_case = NULL;
  union_ctx.has_impl_default = false;
  union_ctx.total_label_count = 0;
  result = idl_set_custom_context(ctx, &union_ctx);
  if (result) return result;
  idl_walk_node_list(ctx, cases, get_py_case_data, IDL_CASE);
  union_ctx.default_label = get_default_discr_value(ctx, union_node);


  idl_file_out_printf(ctx, "@union(%s)\n", union_ctx.discr_type);
  idl_file_out_printf(ctx, "class %s:\n", pyName);

  /* Generate the union content. */
  union_generate_attributes(ctx);
  union_generate_constructor(ctx);

  idl_file_out_printf(ctx, "};\n\n");
  idl_reset_custom_context(ctx);

  for (uint32_t i = 0; i < nr_cases; ++i)
  {
    free(union_ctx.cases[i].name);
    free(union_ctx.cases[i].type_name);
    for (uint32_t j = 0; j < union_ctx.cases[i].label_count; ++j)
    {
      free(union_ctx.cases[i].labels[j]);
    }
    free(union_ctx.cases[i].labels);
  }
  free(union_ctx.cases);
  free(union_ctx.discr_type);
  free(union_ctx.default_label);
  free(pyName);

  idl_set_custom_context(ctx, out_ctx);

  return result;
}

static idl_retcode_t
enumerator_generate_identifier(idl_backend_ctx ctx, const idl_node_t *enumerator_node)
{
  const idl_enumerator_t *enumerator = (const idl_enumerator_t *) enumerator_node;
  char *pyName = get_py_name(idl_identifier(enumerator));
  idl_file_out_printf(ctx, "%s = auto()\n", pyName);
  free(pyName);
  return IDL_RETCODE_OK;
}

static idl_retcode_t
enum_generate_body(idl_backend_ctx ctx, const idl_enum_t *enum_node)
{
  idl_retcode_t result;
  char *pyName = get_py_name(idl_identifier(enum_node));
  const idl_node_t *enumerators = (const idl_node_t *) enum_node->enumerators;

  idl_file_out_printf(ctx, "class %s (Enum):\n", pyName);
  idl_indent_incr(ctx);
  result = idl_walk_node_list(ctx, enumerators, enumerator_generate_identifier, IDL_ENUMERATOR);
  idl_indent_decr(ctx);
  idl_file_out_printf(ctx, "\n");
  free(pyName);
  return result;
}

static idl_retcode_t
typedef_generate_body(idl_backend_ctx ctx, const idl_typedef_t *typedef_node)
{
  char *pyName = get_py_name(idl_identifier(typedef_node->declarators));
  char *pyType = get_py_type(typedef_node->type_spec);

  idl_file_out_printf(ctx, "%s = %s\n\n", pyName, pyType);

  free(pyType);
  free(pyName);
  return IDL_RETCODE_OK;
}

static idl_retcode_t
module_generate_body(idl_backend_ctx ctx, const idl_module_t *module_node)
{
  idl_backend_py_ctx pctx = (idl_backend_py_ctx) idl_get_custom_context(ctx);
  idl_retcode_t result;
  char *pyName = get_py_name(idl_identifier(module_node));
  char *dname = NULL;
  char *fname = NULL;

  if (idl_asprintf(&dname, "%s/%s", pctx->basedir, pyName) == -1)
    return IDL_RETCODE_NO_MEMORY;

  if (idl_asprintf(&fname, "%s/__init__.py", dname) == -1)
    return IDL_RETCODE_NO_MEMORY;

  mkdir(dname, 0770);

  idl_backend_ctx mod_ctx = idl_backend_context_new(4, NULL, NULL);
  idl_backend_py_ctx mod_pctx = (idl_backend_py_ctx) malloc(sizeof(struct idl_backend_py_ctx_s));
  mod_pctx->basedir = dname;
  mod_pctx->target_file = pctx->target_file;
  idl_set_custom_context(mod_ctx, mod_pctx);
  idl_file_out_new(mod_ctx, fname);

  print_py_imports(mod_ctx);

  result = idl_walk_node_list(mod_ctx, module_node->definitions, py_scope_walk, IDL_MASK_ALL);
  idl_file_out_close(mod_ctx);
  idl_reset_custom_context(mod_ctx);

  free(mod_pctx);
  free(pyName);
  free(fname);
  free(dname);

  idl_backend_context_free(mod_ctx);

  return result;
}

static idl_retcode_t
const_generate_body(idl_backend_ctx ctx, const idl_const_t *const_node)
{
  char *pyName = get_py_name(idl_identifier(const_node));
  char *pyType = get_py_type(const_node->type_spec);
  char *pyValue = get_py_const_value((const idl_constval_t *) const_node->const_expr);
  idl_file_out_printf(
      ctx,
      "%s: %s = %s;\n\n",
      pyName,
      pyType,
      pyValue);
  free(pyValue);
  free(pyType);
  free(pyName);
  return IDL_RETCODE_OK;
}

static idl_retcode_t
py_scope_walk(idl_backend_ctx ctx, const idl_node_t *node)
{
  idl_retcode_t result = IDL_RETCODE_OK;

  if (idl_mask(node) & IDL_FORWARD)
  {
    //result = forward_decl_generate_body(ctx, (const idl_forward_t *) node);
  }
  else
  {
    switch (idl_mask(node) & IDL_CATEGORY_MASK)
    {
    case IDL_MODULE:
      result = module_generate_body(ctx, (const idl_module_t *) node);
      break;
    case IDL_STRUCT:
      result = struct_generate_body(ctx, (const idl_struct_t *) node);
      break;
    case IDL_UNION:
      result = union_generate_body(ctx, (const idl_union_t *) node);
      break;
    case IDL_ENUM:
      result = enum_generate_body(ctx, (const idl_enum_t *) node);
      break;
    case IDL_TYPEDEF:
      result = typedef_generate_body(ctx, (const idl_typedef_t *) node);
      break;
    case IDL_CONST:
      result = const_generate_body(ctx, (const idl_const_t *) node);
      break;
    default:
      assert(0);
      break;
    }
  }

  return result;
}

idl_retcode_t
idl_backendGenerateType(idl_backend_ctx ctx, const idl_pstate_t *parse_tree)
{
  return idl_walk_node_list(ctx, parse_tree->root, py_scope_walk, IDL_MASK_ALL);
}

