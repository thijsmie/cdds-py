project(helloworld LANGUAGES C CXX)
cmake_minimum_required(VERSION 3.5)

if(NOT TARGET CycloneDDS-Py::idlpy)
  find_package(CycloneDDS-Py REQUIRED)
endif()

idlpy_generate(TARGET helloworlddata FILES TypeObj.idl)
