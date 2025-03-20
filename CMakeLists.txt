cmake_minimum_required(VERSION 3.16)

project(thesis)

if(NOT DEFINED ENV{THESIS})
    message(STATUS "Using default output directory: ${CMAKE_BINARY_DIR}")
    set(OUT_DIR ${CMAKE_BINARY_DIR})
else()
    message(STATUS "Using custom output directory: $ENV{THESIS}")
    set(OUT_DIR $ENV{THESIS})
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${OUT_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${OUT_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${OUT_DIR}/lib)

add_subdirectory(dataset_generation)