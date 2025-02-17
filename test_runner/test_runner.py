#!/usr/bin/env python3

import os
import sys
from pygit2 import Repository
import sqlite3

class TestRunner:
    def __init__(self, slam_system_name, config_name):
        self.slam_system_name = slam_system_name
        self.config_name = config_name

        self.thesis_repo_path = os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0])) + "/..") # The parent directory of the script should be the thesis repository root.

        self.thesis_repo = Repository(self.thesis_repo_path)
        self.slam_system_repo = Repository(os.path.join(self.thesis_repo_path, "slam_systems", slam_system_name))

        self.connect_db()
        self.insert_test()

    def run(self):
        print(f"Running test for {self.slam_system_name} with config {self.config_name}")

    def connect_db(self):
        self.conn = sqlite3.connect(self.thesis_repo_path + "/test_output/slam_tests.db")

    def insert_test(self):
        cur = self.conn.cursor()
        cur.execute('''
            INSERT INTO tests (slam_system_name, config_name, thesis_hash, slam_system_hash, output_dir, test_result)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.slam_system_name, self.config_name, str(self.thesis_repo.head.target), str(self.slam_system_repo.head.target), self.thesis_repo_path + "/test_output", 0))
        self.conn.commit()
        print(cur.lastrowid)

def usage():
    print("Usage: $ ./test_runner.py <SLAM System Name> <Config Name>")
    print("Example: $ ./test_runner.py ORB_SLAM3 EuRoC_V1_01_mono")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()

    tr = TestRunner(sys.argv[1], sys.argv[2])

    script_directory = os.path.dirname(os.path.abspath(sys.argv[0])) 

    repo = Repository(script_directory)

    print(repo.diff().patch)
    print(repo.head.target)