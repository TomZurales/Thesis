cmake_minimum_required(VERSION 3.22.1 FATAL_ERROR)

project(gz-gui-hello-plugin)

set (CMAKE_AUTOMOC ON)

find_package (Qt5 5.15
  COMPONENTS
    Core
    Quick
    QuickControls2
  REQUIRED
)

# Find the Gazebo GUI library
find_package(gz-gui8 REQUIRED)
set(GZ_GUI_VER ${gz-gui8_VERSION_MAJOR})

qt_add_resources(resources_RCC hello.qrc)

# Generate examples
add_library(HelloPlugin SHARED ${headers_MOC}
  HelloPlugin.cc
  ${resources_RCC}
)
target_link_libraries(HelloPlugin
  gz-gui${GZ_GUI_VER}::gz-gui${GZ_GUI_VER}
)
