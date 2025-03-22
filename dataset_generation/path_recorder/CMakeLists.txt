find_package(gz-sim9 REQUIRED)
find_package(gz-plugin3 REQUIRED COMPONENTS register)
find_package(gz-transport14 REQUIRED)
find_package(gz-math8 REQUIRED)
find_package(gz-physics8 REQUIRED)

add_library(JoystickManager src/JoystickManager.cc)
target_include_directories(JoystickManager PUBLIC include)
target_compile_options(JoystickManager PRIVATE -fPIC)

add_library(ObserverRobotController SHARED src/ObserverRobotController.cc)
target_include_directories(ObserverRobotController PRIVATE include)
target_link_libraries(ObserverRobotController PRIVATE JoystickManager)
target_link_libraries(ObserverRobotController
  PRIVATE gz-plugin3::gz-plugin3
  PRIVATE gz-sim9::gz-sim9
  PRIVATE gz-transport14::gz-transport14
  PRIVATE gz-physics8::gz-physics8
  PRIVATE gz-math8::gz-math8)

# Testing
add_executable(joystick_manager_test test/JoystickManager.cc)
target_link_libraries(joystick_manager_test JoystickManager)

add_executable(observer_robot_controller_test test/ObserverRobotController.cc)
target_link_libraries(observer_robot_controller_test ObserverRobotController)