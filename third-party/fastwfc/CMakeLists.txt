cmake_minimum_required(VERSION 3.14...3.19)

project(fastwfc VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(DEFAULT_BUILD_TYPE "Release")
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# if(MSVC)
#     set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
#     set(BUILD_SHARED_LIBS TRUE)
# endif()

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to '${DEFAULT_BUILD_TYPE}' as none was specified.")
  set(CMAKE_BUILD_TYPE "${DEFAULT_BUILD_TYPE}" CACHE STRING "Choose the type of build." FORCE)
endif()

include(GNUInstallDirs)

set(SOURCE_FILES src/wave.cpp src/propagator.cpp src/wfc.cpp src/run_wfc.cpp)

add_library(${PROJECT_NAME} STATIC ${SOURCE_FILES})

# To link to the static lin (see https://github.com/pybind/cmake_example/issues/11)
set(LIBRARY_OUTPUT_PATH lib CACHE PATH "Build directory" FORCE)

target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/fastwfc> $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

set_target_properties(${PROJECT_NAME} PROPERTIES
  VERSION ${PROJECT_VERSION}
  SOVERSION 1)

set_target_properties(${PROJECT_NAME} PROPERTIES POSITION_INDEPENDENT_CODE ON)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

install(TARGETS ${PROJECT_NAME} EXPORT fastwfcTargets
  ARCHIVE  DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY  DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME  DESTINATION ${CMAKE_INSTALL_BINDIR})

install(DIRECTORY "${PROJECT_SOURCE_DIR}/include/fastwfc" DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

install(EXPORT fastwfcTargets NAMESPACE fastwfc:: DESTINATION share/fastwfc/cmake)

# export(TARGETS ${PROJECT_NAME} FILE fastwfcTargets.cmake)

# Added for python

# The CMake package config and target files are installed under the Python
# package root. This is necessary to ensure that all the relative paths in the
# helloTargets.cmake resolve correctly. It also provides encapsulation.
#
# The actual path used must be selected so that consuming projects can locate it
# via `find_package`. To support finding CMake packages in the Python package
# prefix, using `find_package`s default search path of
# `<prefix>/<name>/share/<name>*/cmake/` is reasonable. Adding the Python
# package installation prefix to CMAKE_PREFIX_PATH in combination with this path
# will allow `find_package` to find this package and any other package installed
# via a Python package if the CMake and Python packages are named the same.
set(FASTWFC_CMAKE_PACKAGE_INSTALL_SUBDIR "share/fastwfc/cmake")

include(CMakePackageConfigHelpers)

write_basic_package_version_file(
  fastwfcTargetsVersion.cmake
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY SameMinorVersion)

configure_package_config_file(
  "${PROJECT_SOURCE_DIR}/cmake/fastwfcTargets.cmake.in" fastwfcTargets.cmake
  INSTALL_DESTINATION ${FASTWFC_CMAKE_PACKAGE_INSTALL_SUBDIR})

install(FILES "${PROJECT_BINARY_DIR}/fastwfcTargets.cmake"
              "${PROJECT_BINARY_DIR}/fastwfcTargetsVersion.cmake"
        DESTINATION ${FASTWFC_CMAKE_PACKAGE_INSTALL_SUBDIR})
