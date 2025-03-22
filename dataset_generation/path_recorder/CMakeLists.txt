find_package(gz-sim8 REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS register)
find_package(gz-transport13 REQUIRED)
find_package(gz-math7 REQUIRED)
find_package(gz-physics7 REQUIRED)

add_library(JoystickPublisher SHARED src/JoystickPublisher.cc)
target_link_libraries(JoystickPublisher
  PRIVATE gz-plugin2::gz-plugin2
  PRIVATE gz-sim8::gz-sim8
  PRIVATE gz-transport13::gz-transport13
  PRIVATE gz-physics7::gz-physics7
  PRIVATE gz-math7::gz-math7)

# add_library(VelocityController SHARED src/VelocityController.cc)
# target_include_directories(VelocityController PRIVATE include)
# set_property(TARGET VelocityController PROPERTY CXX_STANDARD 17)
# target_link_libraries(VelocityController
#   PRIVATE gz-plugin2::gz-plugin2
#   PRIVATE gz-sim8::gz-sim8
#   PRIVATE gz-transport13::gz-transport13
#   PRIVATE gz-physics7::gz-physics7
#   PRIVATE gz-math7::gz-math7)
