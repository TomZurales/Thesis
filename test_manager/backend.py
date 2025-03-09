import os
import pygit2

SLAM_SYSTEMS_DIR= os.path.join(os.path.dirname(__file__), "../slam_systems")

def get_all_slam_systems():
    slam_systems = []
    for item in os.listdir(SLAM_SYSTEMS_DIR):
        if os.path.isdir(os.path.join(SLAM_SYSTEMS_DIR, item)):
            slam_systems.append(item)
    return slam_systems

def get_slam_system_configs(slam_system):
    configs = []
    slam_system_dir = os.path.join(SLAM_SYSTEMS_DIR, slam_system)
    config_dir = os.path.join(slam_system_dir, "test_configs")
    for item in os.listdir(config_dir):
        if os.path.isfile(os.path.join(config_dir, item)):
            configs.append(item)
    return configs

def verify_slam_system(slam_system):
    # Check if the repo has uncommitted changes
    repo = pygit2.Repository(os.path.join(SLAM_SYSTEMS_DIR, slam_system))
    print(repo.status())
    if repo.status():
        return False
    return True

def get_manager_backend_git_hash():
    pass

def get_slam_system_git_hash(slam_system_name):
    pass

def get_dataset_hash(dataset_name):
    pass

def get_manager_version():
    pass

def get_slam_system_version(slam_system_name):
    pass

def get_dataset_version(dataset_name):
    pass

