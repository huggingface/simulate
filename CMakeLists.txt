cmake_minimum_required(VERSION 3.14...3.19)

project(simulate VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(DEFAULT_BUILD_TYPE "Release")
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory("third-party")

# We are using the SKBUILD variable, which is defined when scikit-build is
# running the CMake build, to control building the Python wrapper. This allows
# the C++ project to be installed, standalone, when using the standard CMake
# build flow.
if(DEFINED SKBUILD)
  message(STATUS "Building Python wrapper")

  # prevent an unused variable warning
  set(ignoreMe "${SKBUILD}")

  # call pybind11-config to obtain the root of the cmake package
  execute_process(COMMAND ${PYTHON_EXECUTABLE} -m pybind11 --cmakedir
                  OUTPUT_VARIABLE pybind11_ROOT_RAW)
  string(STRIP ${pybind11_ROOT_RAW} pybind11_ROOT)
  find_package(pybind11)

  pybind11_add_module(_fastwfc MODULE
                      "${PROJECT_SOURCE_DIR}/third-party/fastwfc/fastwfc_py.cpp")

  pybind11_add_module(_vhacd MODULE
                       "${PROJECT_SOURCE_DIR}/third-party/vhacd/vhacd_py.cpp")

  target_link_libraries(_fastwfc PRIVATE fastwfc)
  target_link_libraries(_vhacd PRIVATE vhacd)

  # Installing the extension module to the root of the package
  install(TARGETS _fastwfc DESTINATION .)
  install(TARGETS _vhacd DESTINATION .)

  # configure_file("${PROJECT_SOURCE_DIR}/third-party/fastwfc/__main__.py.in"
  #                "${PROJECT_BINARY_DIR}/src/fastwfc/__main__.py")

  # install(FILES "${PROJECT_BINARY_DIR}/src/fastwfc/__main__.py" DESTINATION .)

  # The extension module must load the fastwfc library as a dependency when the
  # extension module is loaded. The easiest way to locate the fastwfc library is
  # via RPATH. Absolute RPATHs are possible, but they make the resulting
  # binaries not redistributable to other Python installations (conda is broke,
  # wheel reuse is broke, and more!).
  #
  # Placing the fastwfc library in the package and using relative RPATHs that
  # doesn't point outside of the package means that the built package is
  # relocatable. This allows for safe binary redistribution.
  if(APPLE)
    set_target_properties(
      _fastwfc PROPERTIES INSTALL_RPATH "@loader_path/${CMAKE_INSTALL_LIBDIR}")
      set_target_properties(
        _vhacd PROPERTIES INSTALL_RPATH "@loader_path/${CMAKE_INSTALL_LIBDIR}")
    else()
    set_target_properties(_fastwfc PROPERTIES INSTALL_RPATH
                                            "$ORIGIN/${CMAKE_INSTALL_LIBDIR}")
    set_target_properties(_vhacd PROPERTIES INSTALL_RPATH
                                            "$ORIGIN/${CMAKE_INSTALL_LIBDIR}")
  endif()

endif()
