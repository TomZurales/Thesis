install(PROGRAMS test_runner.py
        DESTINATION bin
        RENAME test_runner)

install(PROGRAMS test_runner.py
        DESTINATION bin
        RENAME test_runner)

install(PROGRAMS test_evaluator.py
        DESTINATION bin
        RENAME test_evaluator)

install(PROGRAMS libtest_runner.py libexe_version_manager.py lib_evo.py
        DESTINATION bin)
        
install(DIRECTORY test_configs DESTINATION .)
