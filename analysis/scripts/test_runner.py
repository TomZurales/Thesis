#!/usr/bin/env python3

import asyncio
import heapq
import os
from random import shuffle
import shutil
import subprocess
import sys
from typing import List
# from average import TimedPose, average_poses
import yaml
from libtest_runner import TestConfig, TestInstance
from libexe_version_manager import EXEVersionManager


runtime_root = os.getenv("THESIS_RUNTIME_ROOT")
if not runtime_root:
    raise RuntimeError("THESIS_RUNTIME_ROOT environment variable not set")

os.chdir(runtime_root)

print("Setting up test instances...")

evm = EXEVersionManager()

def get_unrun_tests() -> List[TestInstance]:
    unrun_tests = []
    for config_file in os.listdir("test_configs"):
        if config_file.endswith(".yaml"):
            config = TestConfig.LoadOrCreate(os.path.join("test_configs", config_file))
            unrun_tests.extend(config.getUnrunTests())
    shuffle(unrun_tests)
    return unrun_tests

async def run_test(test: TestInstance):
    print("Starting test:", test)
    result = await test.run_monitored()
    if result:
        print("Test passed:", test)
    else:
        print("Test FAILED:", test)
    return result

async def run_tests_concurrently(tests: List[TestInstance], max_concurrent: int = 10):
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_with_semaphore(test):
        async with semaphore:
            return await run_test(test)
    
    tasks = [run_with_semaphore(test) for test in tests]
    return await asyncio.gather(*tasks)

async def main():
    tests = get_unrun_tests()
    shuffle(tests)
    while len(tests) > 0:
        print(f"Running {len(tests)} tests...")
        
        await run_tests_concurrently(tests)
        
        tests = get_unrun_tests()
        if len(tests) > 0:
            shuffle(tests)
            print(f"{len(tests)} tests did not complete successfully. Re-running...")

    print("All tests complete.")

if __name__ == "__main__":
    asyncio.run(main())