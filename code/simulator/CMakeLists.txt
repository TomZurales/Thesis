cmake_minimum_required(VERSION 3.10)

project(ExistenceEstimationSimulator)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable debugging
# set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_CXX_FLAGS "-O3 -DNDEBUG")

# Find required packages
find_package(Ceres REQUIRED)

# Include directories
include_directories(include)

# Source files
file(GLOB_RECURSE SOURCES "src/*.cc")

# Add executable
add_executable(${PROJECT_NAME} ${SOURCES})

# Link libraries
target_link_libraries(${PROJECT_NAME} ${CERES_LIBRARIES})