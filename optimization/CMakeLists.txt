
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/bin)
find_package(Boost REQUIRED COMPONENTS serialization)

add_executable(characterize_vbee src/characterize_vbee.cc src/world.cc)
target_include_directories(characterize_vbee PRIVATE include)
target_link_libraries(characterize_vbee PRIVATE vbee Boost::serialization)