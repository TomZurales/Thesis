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