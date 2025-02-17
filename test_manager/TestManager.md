# Install
## Dependencies
* pygit2
* imgui

# Test Manager
Test Manager is used to ensure that every test of a SLAM system is accomplished in a repeatable way, with no loss of important data. This is accomplished by recording the current hash of all involved repositories, datasets, and config files at test time to a test database. Additionally, test config files can be used to specify all generated outputs which should be saved.

## Inputs
* SLAM System - The name of the slam system which will run the test (Eg. ORB_SLAM3)
* Configuration - The name of the config to run. Configs are stored in the respective SLAM system

## Database Schema
### Test
* id
* timestamp
* slam_system_name
* config_name
* thesis_hash
* slam_system_hash
* output_dir
* success

## Process
### Pre-Test Checks
If there are any uncommitted changes in either the ```thesis``` or the slam system repositories, a confirmation prompt is given to the user. If the test is continued, the repository/repositories with uncommitted changes will be marked as 'dirty'.

Verify that the SLAM system has a config name matching the given configuration name. If one does not exist, an error is shown and the system exits.

Verify that the config matches the config schema. If it does not, an error is shown and the system exits.

### Collect System State
The current git commit hash of the ```thesis``` repository is recorded, along with the hash of the selectected SLAM system.

The file hash of the config file is recorded and compared to the previous. If the hash is different, the config version is changed accordingly.

The hash of the test_runner binary is recorded and compared to the previous. If the hash is different, the test manager version is changed accordingly.

## Config File Verification
