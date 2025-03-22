find_package(gz-sim8 REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS register)
find_package(gz-transport13 REQUIRED)
find_package(gz-math7 REQUIRED)
find_package(gz-physics7 REQUIRED)

add_library(JoystickManager src/JoystickManager.cc)
target_include_directories(JoystickManager PUBLIC include)

add_library(ObserverRobotController SHARED src/ObserverRobotController.cc)
target_include_directories(ObserverRobotController PRIVATE include)
target_link_libraries(ObserverRobotController PRIVATE JoystickManager)
target_link_libraries(ObserverRobotController
  PRIVATE gz-plugin2::gz-plugin2
  PRIVATE gz-sim8::gz-sim8
  PRIVATE gz-transport13::gz-transport13
  PRIVATE gz-physics7::gz-physics7
  PRIVATE gz-math7::gz-math7)

# Testing
add_executable(joystick_manager_test test/JoystickManager.cc)
target_link_libraries(joystick_manager_test JoystickManager)

add_executable(observer_robot_controller_test test/ObserverRobotController.cc)
target_link_libraries(observer_robot_controller_test ObserverRobotController)