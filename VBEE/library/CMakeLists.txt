FIND_PACKAGE(Eigen3 3.1.0 REQUIRED)

# add_library(vbee SHARED
add_library(vbee
   src/vbee.cc
   src/observability_model.cc
   src/existence_probability_estimator.cc
)
target_include_directories(vbee PUBLIC include)
target_link_libraries(vbee PUBLIC Eigen3::Eigen)

# Debug version of the vbee library
add_library(vbee_debug
   src/vbee.cc
   src/observability_model.cc
   src/existence_probability_estimator.cc
)
target_include_directories(vbee_debug PUBLIC include)
target_link_libraries(vbee_debug PUBLIC Eigen3::Eigen)
set_target_properties(vbee_debug PROPERTIES COMPILE_OPTIONS "")
target_compile_options(vbee_debug PRIVATE -O0 -g)

find_package(GTest REQUIRED)

add_executable(vbee_tests testing/vbee_tests.cc)
target_include_directories(vbee_tests PRIVATE include)
target_link_libraries(vbee_tests PRIVATE vbee_debug GTest::gtest GTest::gtest_main)
set_target_properties(vbee_tests PROPERTIES COMPILE_OPTIONS "")
target_compile_options(vbee_tests PRIVATE -O0 -g)