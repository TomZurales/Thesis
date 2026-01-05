from datetime import datetime
import os
from typing import List, Tuple
from typing_extensions import Literal
from pathvalidate import sanitize_filename
import shutil
import hashlib
import yaml

runtime_root = os.getenv("THESIS_RUNTIME_ROOT")

if not runtime_root:
    raise RuntimeError("THESIS_RUNTIME_ROOT environment variable not set")

def get_file_hash(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


class EXEVersionManager:
    exe_versions: dict[int, str]

    def __init__(self):
        if not os.path.exists(os.path.join(runtime_root, ".aux", "exe_versions.yaml")):
            # First time running, version 1 is the current exe hash
            self.exe_versions = {}
            self.exe_versions[1] = get_file_hash(os.path.join(runtime_root, "bin", "ORB_SLAM3_VBEE"))
            with open(os.path.join(runtime_root, ".aux", "exe_versions.yaml"), 'w') as f:
                yaml.safe_dump(self.exe_versions, f)
        else:
            with open(os.path.join(runtime_root, ".aux", "exe_versions.yaml"), 'r') as f:
                self.exe_versions = yaml.safe_load(f)

    def getLatestResultsRoot(self) -> str:
        latest_version = self.getLatestVersion()[0]
        latest_path = os.path.join(runtime_root, "test_results", f"v{latest_version}")
        if not os.path.exists(latest_path):
            os.makedirs(latest_path)
            shutil.copy2(os.path.join(runtime_root, "bin", "ORB_SLAM3_VBEE"), os.path.join(latest_path, "ORB_SLAM3_VBEE"))
        return latest_path


    def getLatestVersion(self) -> Tuple[int, str]:
        current_hash = get_file_hash(os.path.join(runtime_root, "bin", "ORB_SLAM3_VBEE"))
        if self.exe_versions[max(self.exe_versions.keys())] != current_hash:
            print("New SLAM executable detected, creating new version entry and copying executable.")
            new_version = max(self.exe_versions.keys()) + 1
            self.exe_versions[new_version] = current_hash
            with open(os.path.join(runtime_root, ".aux", "exe_versions.yaml"), 'w') as f:
                yaml.safe_dump(self.exe_versions, f)
            return new_version, current_hash
        return max(self.exe_versions.keys()), current_hash

    def getPathForVersion(self, version: int) -> str:
        return os.path.join(runtime_root, "test_results", f"v{version}")
    
    def getEXEPathForVersion(self, version: int) -> str:
        return os.path.join(self.getPathForVersion(version), "ORB_SLAM3_VBEE")