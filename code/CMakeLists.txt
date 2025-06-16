cmake_minimum_required(VERSION 3.14)
project(PointProbabilityEngine VERSION 1.0.0 LANGUAGES C CXX)

# Find required packages
find_package(Eigen3 REQUIRED)
find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)
find_package(glm REQUIRED)

# Add GLAD as a static library
set(GLAD_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/third_party/glad)
add_library(glad STATIC ${GLAD_SOURCE_DIR}/src/glad.c)
target_include_directories(glad PUBLIC ${GLAD_SOURCE_DIR}/include)
set_target_properties(glad PROPERTIES
    C_STANDARD 11
    C_STANDARD_REQUIRED ON
    POSITION_INDEPENDENT_CODE ON
)

# Add library source files here
add_library(PointProbabilityEngine SHARED
  src/PointProbabilityEngine.cc
  src/Camera.cc
  src/IcosMetadata.cc
  src/Visualizer.cpp
  src/Icosahedron.cc
)

target_include_directories(PointProbabilityEngine
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
    ${EIGEN3_INCLUDE_DIR}
    ${OPENGL_INCLUDE_DIR}
    ${GLFW_INCLUDE_DIRS}
    ${GLM_INCLUDE_DIRS}
    ${GLAD_SOURCE_DIR}/include
)

target_link_libraries(PointProbabilityEngine
  PUBLIC 
    Eigen3::Eigen
    OpenGL::GL
    glfw
    glad
    ${CMAKE_DL_LIBS}
)

set_target_properties(PointProbabilityEngine PROPERTIES
  VERSION ${PROJECT_VERSION}
  SOVERSION 1
  CXX_STANDARD 23
  CXX_STANDARD_REQUIRED ON
  POSITION_INDEPENDENT_CODE ON
)

# Add demo executables
add_executable(demo demo/demo.cc)
target_link_libraries(demo PointProbabilityEngine)

add_executable(visualizer_demo demo/visualizer_demo.cc)
target_link_libraries(visualizer_demo PointProbabilityEngine)
