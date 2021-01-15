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
include(GenerateExportHeader)

add_library(
  idlpy SHARED
    src/backend.c
    src/backendPyUtils.c
    src/backendPyType.c
    src/idl_ostream.c
    src/generator.c)

target_include_directories(
  idlpy
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/include>)

target_link_libraries(idlpy PUBLIC CycloneDDS::idl)

generate_export_header(
  idlpy
  BASE_NAME IDLPY_EXPORT
  EXPORT_MACRO_NAME IDLPY_EXPORT
  EXPORT_FILE_NAME "include/idlpy/export.h")

add_library(${PROJECT_NAME}::idlpy ALIAS idlpy)

install(
  TARGETS idlpy
  EXPORT "${CMAKE_PROJECT_NAME}"
  RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}" COMPONENT idlpy
  LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}" COMPONENT idlpy
  ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}" COMPONENT idlpy)

install(
  FILES Generate.cmake
  DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${PROJECT_NAME}/idlpy"
  COMPONENT idlpy)

include(Generate.cmake)
