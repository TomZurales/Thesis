#!/bin/bash

# Function to handle cleanup when script is stopped
stop_auto_committer() {
    echo -e "\n\033[33mStopping auto-committer and creating final commit on master branch...\033[0m"
    
    # Save the current branch name
    current_branch=$(git rev-parse --abbrev-ref HEAD)
    
    # First, make sure we're on work-log and commit any final changes
    if [ "$current_branch" != "work-log" ]; then
        echo -e "\033[32mSwitching to work-log to finalize changes...\033[0m"
        git checkout work-log
    fi
    
    # Commit any remaining uncommitted changes on work-log
    status=$(git status --porcelain documents/)
    if [ -n "$status" ]; then
        echo -e "\033[32mCommitting final changes to work-log branch...\033[0m"
        git add documents/
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        git commit -m "Automated commit: final changes in documents/ directory at $timestamp"
    fi
    
    # Switch to master branch
    echo -e "\033[32mSwitching to master branch...\033[0m"
    git checkout master
    
    # Merge only the documents/ directory from work-log to master
    echo -e "\033[32mMerging documents/ changes from work-log to master...\033[0m"
    
    # Use git checkout to bring the documents/ directory from work-log to master
    git checkout work-log -- documents/
    
    # Check if there are any changes to commit on master
    master_status=$(git status --porcelain documents/)
    if [ -n "$master_status" ]; then
        echo -e "\033[32mCommitting final version to master branch...\033[0m"
        git add documents/
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        git commit -m "Final commit: Writing session completed at $timestamp"
        echo -e "\033[32mFinal commit created successfully on master branch!\033[0m"
    else
        echo -e "\033[33mNo changes to commit to master branch (documents/ already up to date).\033[0m"
    fi
    
    echo -e "\033[32mAuto-committer stopped. Changes successfully transferred to master branch.\033[0m"
    exit 0
}

# Set up signal handlers for Ctrl+C and script termination
trap stop_auto_committer SIGINT SIGTERM EXIT

echo -e "\033[36mAuto-committer started. Press Ctrl+C to stop and create final commit on master branch.\033[0m"
echo -e "\033[36mMonitoring documents/ directory for changes every 10 seconds...\033[0m"

while true; do
    # Save the current branch name
    current_branch=$(git rev-parse --abbrev-ref HEAD)

    if [ "$current_branch" != "work-log" ]; then
        git checkout work-log
    fi

    # Check for changes in documents/
    status=$(git status --porcelain documents/)
    if [ -n "$status" ]; then
        git add documents/
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        git commit -m "Automated commit: changes in documents/ directory at $timestamp"
        echo -e "\033[90mCommitted changes to work-log branch at $timestamp\033[0m"
    fi

    sleep 10
done