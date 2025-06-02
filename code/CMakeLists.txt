cmake_minimum_required(VERSION 3.14)
project(PointProbabilityEngine VERSION 1.0.0 LANGUAGES CXX)

# Find Eigen3
find_package(Eigen3 REQUIRED)

# Add library source files here
add_library(PointProbabilityEngine SHARED
  src/PointProbabilityEngine.cc
  src/Camera.cc
  src/IcosMetadata.cc
)

target_include_directories(PointProbabilityEngine
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    ${EIGEN3_INCLUDE_DIR}
)

target_link_libraries(PointProbabilityEngine
  PUBLIC Eigen3::Eigen
)

set_target_properties(PointProbabilityEngine PROPERTIES
  VERSION ${PROJECT_VERSION}
  SOVERSION 1
  CXX_STANDARD 23
  CXX_STANDARD_REQUIRED ON
)

add_executable(demo demo/demo.cc)
target_link_libraries(demo PointProbabilityEngine)