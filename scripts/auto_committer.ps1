# Function to handle cleanup when script is stopped
function Stop-AutoCommitter {
    Write-Host "`nStopping auto-committer and creating final commit on master branch..." -ForegroundColor Yellow
    
    # Save the current branch name
    $currentBranch = git rev-parse --abbrev-ref HEAD
    
    # First, make sure we're on work-log and commit any final changes
    if ($currentBranch -ne "work-log") {
        Write-Host "Switching to work-log to finalize changes..." -ForegroundColor Green
        git checkout work-log
    }
    
    # Commit any remaining uncommitted changes on work-log
    $status = git status --porcelain documents/
    if ($status) {
        Write-Host "Committing final changes to work-log branch..." -ForegroundColor Green
        git add documents/
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        git commit -m "Automated commit: final changes in documents/ directory at $timestamp"
    }
    
    # Switch to master branch
    Write-Host "Switching to master branch..." -ForegroundColor Green
    git checkout master
    
    # Merge only the documents/ directory from work-log to master
    Write-Host "Merging documents/ changes from work-log to master..." -ForegroundColor Green
    
    # Use git checkout to bring the documents/ directory from work-log to master
    git checkout work-log -- documents/
    
    # Check if there are any changes to commit on master
    $masterStatus = git status --porcelain documents/
    if ($masterStatus) {
        Write-Host "Committing final version to master branch..." -ForegroundColor Green
        git add documents/
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        git commit -m "Final commit: Writing session completed at $timestamp"
        Write-Host "Final commit created successfully on master branch!" -ForegroundColor Green
    } else {
        Write-Host "No changes to commit to master branch (documents/ already up to date)." -ForegroundColor Yellow
    }
    
    Write-Host "Auto-committer stopped. Changes successfully transferred to master branch." -ForegroundColor Green
    exit 0
}

# Use PowerShell's trap statement to catch any termination
trap {
    Stop-AutoCommitter
}

Write-Host "Auto-committer started. Press Ctrl+C to stop and create final commit on master branch." -ForegroundColor Cyan
Write-Host "Monitoring documents/ directory for changes every 10 seconds..." -ForegroundColor Cyan

try {
    while ($true) {
        # Save the current branch name
        $currentBranch = git rev-parse --abbrev-ref HEAD

        if ($currentBranch -ne "work-log") {
            git checkout work-log
        }

        # Check for changes in documents/
        $status = git status --porcelain documents/
        if ($status) {
            git add documents/
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            git commit -m "Automated commit: changes in documents/ directory at $timestamp"
            Write-Host "Committed changes to work-log branch at $timestamp" -ForegroundColor DarkGray
        }

        Start-Sleep -Seconds 10
    }
}
finally {
    # This finally block ALWAYS runs when the script exits, regardless of how it exits
    Stop-AutoCommitter
}