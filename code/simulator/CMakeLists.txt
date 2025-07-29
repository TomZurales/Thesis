cmake_minimum_required(VERSION 3.10)

project(ExistenceEstimationSimulator)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable debugging
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")

# Include directories
include_directories(include)

# Source files
file(GLOB_RECURSE SOURCES "src/*.cc")

# Add executable
add_executable(${PROJECT_NAME} ${SOURCES})