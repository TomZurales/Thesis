find_package(Boost REQUIRED COMPONENTS serialization)
find_package(Pangolin REQUIRED)

add_library(observability_scenario src/observability_scenario.cc)
target_include_directories(observability_scenario PUBLIC include)
target_link_libraries(observability_scenario PUBLIC Boost::serialization)
# target_compile_options(observability_scenario PRIVATE -O0 -g)

add_executable(vbee_tester src/vbee_tester.cc)
target_link_libraries(vbee_tester observability_scenario vbee)
target_include_directories(vbee_tester PRIVATE include)
# target_compile_options(vbee_tester PRIVATE -O0 -g)


install(PROGRAMS scripts/test_runner.py
        DESTINATION bin
        RENAME test_runner)

install(PROGRAMS scripts/test_runner.py
        DESTINATION bin
        RENAME test_runner)

install(PROGRAMS scripts/test_evaluator.py
        DESTINATION bin
        RENAME test_evaluator)

install(PROGRAMS scripts/libtest_runner.py scripts/libexe_version_manager.py scripts/lib_evo.py
        DESTINATION bin)
        
install(DIRECTORY test_configs DESTINATION .)
