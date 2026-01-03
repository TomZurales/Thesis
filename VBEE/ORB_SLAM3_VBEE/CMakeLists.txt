set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(yaml-cpp REQUIRED)

set(SUFFIX "")
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(SUFFIX "_debug")
endif()

add_executable(ORB_SLAM3_VBEE${SUFFIX} src/stereo_vbee.cc)
target_link_libraries(ORB_SLAM3_VBEE${SUFFIX} PRIVATE ORB_SLAM3 ${YAML_CPP_LIBRARIES})
target_include_directories(ORB_SLAM3_VBEE${SUFFIX} PRIVATE ${YAML_CPP_INCLUDE_DIR})
install(TARGETS ORB_SLAM3_VBEE${SUFFIX}
    RUNTIME DESTINATION bin
)