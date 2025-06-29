cmake_minimum_required(VERSION 3.14)
project(PointProbabilityEngine VERSION 1.0.0 LANGUAGES C CXX)
# Set build type to Release with maximum optimizations if not specified
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# Enable maximum optimizations
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -DNDEBUG")
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -O3 -DNDEBUG")

# Additional optimization flags for GCC/Clang
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -march=native -mtune=native")
  set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -march=native -mtune=native")
endif()
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
  src/IcosahedronBackend.cc
  # src/Visualizer.cc
  src/Icosahedron.cc
  src/Utility.cc
  src/Viewer.cc
  src/ShaderManager.cc
  src/PointProbabilityEngine/3DView.cc

  # Graphics files
  src/Graphics/FloorPlane.cc
  src/Graphics/PointCloud.cc
  src/Graphics/IcosModel.cc
  # src/Graphics/CenteredPoint.cc
  
  # Imgui files
  third_party/imgui/imgui.cpp
  third_party/imgui/imgui_draw.cpp
  third_party/imgui/imgui_widgets.cpp
  third_party/imgui/imgui_demo.cpp
  third_party/imgui/imgui_tables.cpp
  third_party/imgui/backends/imgui_impl_glfw.cpp
  third_party/imgui/backends/imgui_impl_opengl3.cpp
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
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/imgui
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
