#
# Copyright(c) 2020 ADLINK Technology Limited and others
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v. 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Eclipse Distribution License
# v. 1.0 which is available at
# http://www.eclipse.org/org/documents/edl-v10.php.
#
# SPDX-License-Identifier: EPL-2.0 OR BSD-3-Clause
#

function(IDLPY_GENERATE)
  cmake_parse_arguments(IDLPY "" "TARGET" "FILES" "" ${ARGN})

  if(NOT IDLPY_TARGET)
    message(FATAL_ERROR "idlpy_generate was called without TARGET")
  endif()
  if(NOT IDLPY_FILES)
    message(FATAL_ERROR "idlpy_generate was called without FILES")
  endif()

  set(_dir ${CMAKE_CURRENT_BINARY_DIR})
  set(_target ${IDLPY_TARGET})
  foreach(_file ${IDLPY_FILES})
    get_filename_component(_path ${_file} ABSOLUTE)
    get_filename_component(_name ${_file} NAME_WE)
    set(_source "${_dir}/${_name}/__init__.py")
    list(APPEND _sources "${_source}")
    add_custom_command(
      OUTPUT "${_source}"
      COMMAND $<TARGET_FILE:CycloneDDS::idlc>
      ARGS -l $<TARGET_FILE:CycloneDDS-Py::idlpy> ${_path})
  endforeach()

  add_custom_target("${_target}" ALL DEPENDS ${_sources})
endfunction()
