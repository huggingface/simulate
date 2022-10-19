cmake_minimum_required(VERSION 3.14)

project("vhacd"
    VERSION 0.0.1
    LANGUAGES CXX
)

add_library(vhacd INTERFACE)

include(GNUInstallDirs)

target_include_directories(vhacd INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/vhacd> $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

target_compile_features(
    vhacd 
    INTERFACE 
        cxx_std_17)

install(TARGETS vhacd
        EXPORT vhacdTargets
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})

include(CMakePackageConfigHelpers)
write_basic_package_version_file("vhacdConfigVersion.cmake"
                                 VERSION ${PROJECT_VERSION}
                                 COMPATIBILITY SameMajorVersion)

configure_package_config_file(
  "${PROJECT_SOURCE_DIR}/cmake/vhacdConfig.cmake.in"
  "${PROJECT_BINARY_DIR}/vhacdConfig.cmake"
  INSTALL_DESTINATION
  ${CMAKE_INSTALL_DATAROOTDIR}/cmake/vhacd)

install(EXPORT vhacdTargets
        FILE vhacdTargets.cmake
        NAMESPACE vhacd::
        DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/vhacd)

install(FILES "${PROJECT_BINARY_DIR}/vhacdConfig.cmake"
              "${PROJECT_BINARY_DIR}/vhacdConfigVersion.cmake"
        DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/vhacd)

install(DIRECTORY ${PROJECT_SOURCE_DIR}/include/vhacd DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

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
set(VHACD_CMAKE_PACKAGE_INSTALL_SUBDIR "share/vhacd/cmake")

include(CMakePackageConfigHelpers)

write_basic_package_version_file(
  vhacdTargetsVersion.cmake
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY SameMinorVersion)

configure_package_config_file(
  "${PROJECT_SOURCE_DIR}/cmake/vhacdTargets.cmake.in" vhacdTargets.cmake
  INSTALL_DESTINATION ${VHACD_CMAKE_PACKAGE_INSTALL_SUBDIR})

install(FILES "${PROJECT_BINARY_DIR}/vhacdTargets.cmake"
              "${PROJECT_BINARY_DIR}/vhacdTargetsVersion.cmake"
        DESTINATION ${VHACD_CMAKE_PACKAGE_INSTALL_SUBDIR})
