#!/usr/bin/env python3

import sqlite3
import os
import sys

thesis_repo_path = os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0])) + "/..") # The parent directory of the script should be the thesis repository root.

def init_db():
    if(os.path.exists(thesis_repo_path + "/test_output/slam_tests.db")):
        print("Database already exists. Exiting.")
        return
    conn = sqlite3.connect(thesis_repo_path + "/test_output/slam_tests.db")
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            slam_system_name TEXT,
            config_name TEXT,
            thesis_hash TEXT,
            slam_system_hash TEXT,
            output_dir TEXT,
            test_result INTEGER
        )
    ''')

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")