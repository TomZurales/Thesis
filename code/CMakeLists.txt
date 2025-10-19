cmake_minimum_required(VERSION 3.14)
project(PointProbabilityEngine VERSION 1.0.0 LANGUAGES CXX C)

# Find Eigen3
find_package(Eigen3 REQUIRED)

# Find GLFW3
find_package(glfw3 REQUIRED)

# Add GLAD as a separate static library
add_library(glad STATIC
  third_party/glad/src/glad.c
)

set_target_properties(glad PROPERTIES
  C_STANDARD 11
  C_STANDARD_REQUIRED ON
  POSITION_INDEPENDENT_CODE ON
)

target_include_directories(glad
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/glad/include
)

# Add main library source files
add_library(PointProbabilityEngine SHARED
  src/PointProbabilityEngine.cc
  src/Camera.cc
  src/IcosMetadata.cc
  src/Visualizer.cc
)

target_include_directories(PointProbabilityEngine
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    ${EIGEN3_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/glad/include
)

target_link_libraries(PointProbabilityEngine
  PUBLIC 
    Eigen3::Eigen
    glfw
    glad
)

set_target_properties(PointProbabilityEngine PROPERTIES
  VERSION ${PROJECT_VERSION}
  SOVERSION 1
  CXX_STANDARD 23
  CXX_STANDARD_REQUIRED ON
)

add_executable(demo demo/demo.cc)
target_link_libraries(demo PointProbabilityEngine)

# Copy shader files to build directory
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/src/shaders DESTINATION ${CMAKE_CURRENT_BINARY_DIR})