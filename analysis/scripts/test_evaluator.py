#!/usr/bin/env python3

from multiprocessing import Pool
from typing import List
from lib_evo import generate_evo_stats, aggregateEvoStats
from libtest_runner import TestConfig, TestInstance
import os

def evaluate_test(test: TestInstance):
    print("Evaluating test:", test)
    try:
        generate_evo_stats(test)
        print("Evaluation complete for test:", test)
    except Exception as e:
        print("Evaluation FAILED for test:", test, "Error:", e)

def get_unevaluated_tests() -> List[TestInstance]:
    unevaluated_tests = []
    for config_file in os.listdir("test_configs"):
        if config_file.endswith(".yaml"):
            config = TestConfig.LoadOrCreate(os.path.join("test_configs", config_file))
            unevaluated_tests.extend(config.getUnevaluatedTests())
    return unevaluated_tests

os.chdir(os.getenv("THESIS_RUNTIME_ROOT"))

unevaluated_tests = get_unevaluated_tests()

with Pool(10) as p:
    p.map(evaluate_test, unevaluated_tests)

print("All evaluations complete.")

for config_file in os.listdir("test_configs"):
        if config_file.endswith(".yaml"):
            config = TestConfig.LoadOrCreate(os.path.join("test_configs", config_file))
            aggregateEvoStats(config)