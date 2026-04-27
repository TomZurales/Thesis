cmake_minimum_required(VERSION 3.16)

project(thesis)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug)
endif()

if(NOT DEFINED ENV{THESIS_RUNTIME_DIR})
    message(STATUS "Using default runtime directory: ~/thesis_runtime")
    set(OUT_DIR $ENV{HOME}/thesis_runtime)
else()
    message(STATUS "Using custom output directory: $ENV{THESIS_RUNTIME_DIR}")
    set(OUT_DIR $ENV{THESIS_RUNTIME_DIR})
endif()

set(CMAKE_INSTALL_PREFIX ${OUT_DIR})

# add_subdirectory(deps/DBoW2)
# add_subdirectory(deps/g2o)
# add_subdirectory(deps/Sophus)
# add_subdirectory(VBEE/library)
# add_subdirectory(libVBEE)
add_subdirectory(ORB-SLAM3_VBEE)
# add_subdirectory(VBEE)
# add_subdirectory(analysis)
# add_subdirectory(optimization)

add_custom_target(update_requirements ALL
    COMMAND /bin/bash -c "source ${CMAKE_SOURCE_DIR}/.venv/bin/activate; pip freeze > ${CMAKE_SOURCE_DIR}/.aux/requirements.txt" VERBATIM
    COMMENT "Updating requirements.txt with current pip packages"
)

install(DIRECTORY .aux/
    DESTINATION .aux
)