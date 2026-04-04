set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(yaml-cpp REQUIRED)

set(SUFFIX "")
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(SUFFIX "_debug")
endif()

add_executable(ORB_SLAM3_VBEE src/stereo_vbee.cc)
target_link_libraries(ORB_SLAM3_VBEE PRIVATE ORB_SLAM3 ${YAML_CPP_LIBRARIES})
target_include_directories(ORB_SLAM3_VBEE PRIVATE ${YAML_CPP_INCLUDE_DIR})

# Debug version of the ORB_SLAM3_VBEE executable
add_executable(ORB_SLAM3_VBEE_debug src/stereo_vbee.cc)
target_link_libraries(ORB_SLAM3_VBEE_debug PRIVATE ORB_SLAM3_debug ${YAML_CPP_LIBRARIES})
target_include_directories(ORB_SLAM3_VBEE_debug PRIVATE ${YAML_CPP_INCLUDE_DIR})
set_target_properties(ORB_SLAM3_VBEE_debug PROPERTIES COMPILE_OPTIONS "")
target_compile_options(ORB_SLAM3_VBEE_debug PRIVATE -O0 -g)

install(TARGETS ORB_SLAM3_VBEE ORB_SLAM3_VBEE_debug
    RUNTIME DESTINATION bin
)