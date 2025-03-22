find_package(gz-sim8 REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS register)
find_package(gz-transport13 REQUIRED)
find_package(gz-math7 REQUIRED)
find_package(gz-physics7 REQUIRED)

add_library(JoystickManager SHARED src/JoystickManager.cc)

target_include_directories(JoystickManager PUBLIC include)