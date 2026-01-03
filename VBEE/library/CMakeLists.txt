FIND_PACKAGE(Eigen3 3.1.0 REQUIRED)

# add_library(vbee SHARED
add_library(vbee
   src/vbee.cc
   src/observability_model.cc
   src/existence_probability_estimator.cc
)
target_include_directories(vbee PUBLIC include)
target_link_libraries(vbee PUBLIC Eigen3::Eigen)