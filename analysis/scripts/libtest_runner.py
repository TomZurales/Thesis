import asyncio
from datetime import datetime
import os
import subprocess
from typing import List
from typing_extensions import Literal
from pathvalidate import sanitize_filename
import yaml
from libexe_version_manager import EXEVersionManager

runtime_root = os.getenv("THESIS_RUNTIME_ROOT")

if not runtime_root:
    raise RuntimeError("THESIS_RUNTIME_ROOT environment variable not set")

def to_filename(s: str) -> str:
    return sanitize_filename(s.replace(" ", "_").replace("+", "and"))

evm = EXEVersionManager()

class TestInstance:
    version: int
    name: str
    dataset: str
    mode: str
    iteration: int
    cwd: str
    
    n: int
    k: int
    distance_threshold: float
    unknown_psge_value: float
    min_confidence_threshold: float
    max_error_threshold: float
    init_p_e: float
    bad_threshold: float
    damping_coeff: float
    init_observability: float
    observability_damping_coeff: float
    sigmoid_midpoint: float
    sigmoid_steepness: float
    falseNegativeRate: float
    falsePositiveRate: float

    started: datetime | None
    completed: datetime | None
    status: Literal["not_started", "running", "completed", "failed"]
    
    def __init__(self, test_instance_dict: dict):
        self.version = test_instance_dict.get("version")
        self.name = to_filename(test_instance_dict.get("name"))
        self.dataset = test_instance_dict.get("dataset")
        self.mode = test_instance_dict.get("mode")
        self.iteration = test_instance_dict.get("iteration")

        self.n = test_instance_dict.get("n")
        self.k = test_instance_dict.get("k")
        self.distance_threshold = test_instance_dict.get("distance_threshold")
        self.unknown_psge_value = test_instance_dict.get("unknown_psge_value")
        self.min_confidence_threshold = test_instance_dict.get("min_confidence_threshold")
        self.max_error_threshold = test_instance_dict.get("max_error_threshold")
        self.init_p_e = test_instance_dict.get("init_p_e")
        self.bad_threshold = test_instance_dict.get("bad_threshold")
        self.damping_coeff = test_instance_dict.get("damping_coeff")
        self.init_observability = test_instance_dict.get("init_observability")
        self.observability_damping_coeff = test_instance_dict.get("observability_damping_coeff")
        self.sigmoid_midpoint = test_instance_dict.get("sigmoid_midpoint")
        self.sigmoid_steepness = test_instance_dict.get("sigmoid_steepness")
        self.falseNegativeRate = test_instance_dict.get("falseNegativeRate")
        self.falsePositiveRate = test_instance_dict.get("falsePositiveRate")

        self.started = datetime.fromisoformat(test_instance_dict.get("started")) if test_instance_dict.get("started") else None
        self.completed = datetime.fromisoformat(test_instance_dict.get("completed")) if test_instance_dict.get("completed") else None
        self.status = test_instance_dict.get("status", "not_started")

    @staticmethod
    def from_file(path: str) -> 'TestInstance':
        with open(path, 'r') as f:
            instance_dict = yaml.safe_load(f)
        return TestInstance(instance_dict)
    
    def to_file(self, path: str) -> None:
        instance_dict = {
            'version': self.version,
            'name': self.name,
            'dataset': self.dataset,
            'mode': self.mode,
            'iteration': self.iteration,

            'n': self.n,
            'k': self.k,
            'distance_threshold': self.distance_threshold,
            'unknown_psge_value': self.unknown_psge_value,
            'min_confidence_threshold': self.min_confidence_threshold,
            'max_error_threshold': self.max_error_threshold,
            'init_p_e': self.init_p_e,
            'bad_threshold': self.bad_threshold,
            'damping_coeff': self.damping_coeff,
            'init_observability': self.init_observability,
            'observability_damping_coeff': self.observability_damping_coeff,
            'sigmoid_midpoint': self.sigmoid_midpoint,
            'sigmoid_steepness': self.sigmoid_steepness,
            'falseNegativeRate': self.falseNegativeRate,
            'falsePositiveRate': self.falsePositiveRate,

            'started': self.started.isoformat() if self.started else None,
            'completed': self.completed.isoformat() if self.completed else None,
            'status': self.status,
        }
        with open(path, 'w') as f:
            yaml.safe_dump(instance_dict, f)

    def run(self):
        success = False
        self.status = "running"
        self.started = datetime.now()
        self.to_file(self.getInstanceFilePath())

        cwd = self.getCwd()
        with open(os.path.join(cwd, "log.txt"), "w") as log_file:
            subprocess.run([
            evm.getEXEPathForVersion(self.version),
            self.getInstanceFilePath()
            ], cwd=cwd, stdout=log_file, stderr=subprocess.STDOUT, timeout=30*60)
        
        if os.path.exists(os.path.join(cwd, "CameraTrajectory.txt")) and os.path.exists(os.path.join(cwd, "KeyFrameTrajectory.txt")):
            self.status = "completed"
            self.completed = datetime.now()
            success = True
        else:
            self.status = "failed"

        self.to_file(self.getInstanceFilePath())

        return success
    
    async def run_monitored(self):
        success = False
        self.status = "running"
        self.started = datetime.now()
        self.to_file(self.getInstanceFilePath())

        cwd = self.getCwd()
        
        # Start subprocess asynchronously
        with open(os.path.join(cwd, "log.txt"), "w") as log_file:
            process = await asyncio.create_subprocess_exec(
                evm.getEXEPathForVersion(self.version),
                self.getInstanceFilePath(),
                cwd=cwd,
                stdout=log_file,
                stderr=asyncio.subprocess.STDOUT
            )
        
        consecutive_zeros = 0
        heartbeat_path = os.path.join(cwd, "heartbeat.txt")
        
        try:
            while process.returncode is None:
                # Wait 5 seconds
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                    break  # Process finished
                except asyncio.TimeoutError:
                    pass  # Continue monitoring
                
                # Check heartbeat
                try:
                    with open(heartbeat_path, 'r') as f:
                        content = f.read().strip()
                    
                    if content == '-1': # System is still initializing
                        continue
                    # Overwrite with zero
                    with open(heartbeat_path, 'w') as f:
                        f.write('0')
                    
                    if content == '0':
                        consecutive_zeros += 1
                        if consecutive_zeros >= 5:
                            print(f"No heartbeat detected for {consecutive_zeros * 5} seconds. Killing process with SIGKILL.")
                            process.kill()  # Immediate kill -9
                            await process.wait()
                            break
                    else:
                        consecutive_zeros = 0  # Reset counter
                        
                except FileNotFoundError:
                    # Heartbeat file doesn't exist yet
                    consecutive_zeros += 1
                    if consecutive_zeros >= 5:
                        print(f"Heartbeat file not found for {consecutive_zeros * 5} seconds. Killing process with SIGKILL.")
                        process.kill()  # Immediate kill -9
                        await process.wait()
                        break
                except Exception as e:
                    print(f"Error reading heartbeat: {e}")
                    consecutive_zeros += 1
        
        except Exception as e:
            print(f"Error during monitoring: {e}")
            if process.returncode is None:
                process.kill()  # Immediate kill -9
                await process.wait()
        
        # Determine success same as run method
        if os.path.exists(os.path.join(cwd, "CameraTrajectory.txt")) and os.path.exists(os.path.join(cwd, "KeyFrameTrajectory.txt")):
            self.status = "completed"
            self.completed = datetime.now()
            success = True
        else:
            self.status = "failed"

        self.to_file(self.getInstanceFilePath())
        return success

    def getCwd(self) -> str:
        return os.path.join(evm.getPathForVersion(self.version), self.name, self.dataset, self.mode, str(self.iteration))
    
    def getInstanceFilePath(self) -> str:
        return os.path.join(self.getCwd(), "instance.yaml")

    def __str__(self) -> str:
        return f"TestInstance(dataset={self.dataset}, mode={self.mode}, iteration={self.iteration})"

class TestConfig:
    name: str
    datasets: set[str]
    modes: set[str]
    iterations: int
    created: datetime
    last_run: datetime
    
    def __init__(self, test_config_dict: dict):
        # Test Configuration
        self.name = test_config_dict.get("name")
        self.datasets = set(test_config_dict.get("datasets"))
        self.modes = set(test_config_dict.get("modes"))
        self.iterations = test_config_dict.get("iterations")

        # VBEE Configuration
        self.n = test_config_dict.get("n")
        self.k = test_config_dict.get("k")
        self.distance_threshold = test_config_dict.get("distance_threshold")
        self.unknown_psge_value = test_config_dict.get("unknown_psge_value")
        self.min_confidence_threshold = test_config_dict.get("min_confidence_threshold")
        self.max_error_threshold = test_config_dict.get("max_error_threshold")
        self.init_p_e = test_config_dict.get("init_p_e")
        self.bad_threshold = test_config_dict.get("bad_threshold")
        self.damping_coeff = test_config_dict.get("damping_coeff")
        self.init_observability = test_config_dict.get("init_observability")
        self.observability_damping_coeff = test_config_dict.get("observability_damping_coeff")
        self.sigmoid_midpoint = test_config_dict.get("sigmoid_midpoint")
        self.sigmoid_steepness = test_config_dict.get("sigmoid_steepness")
        self.falseNegativeRate = test_config_dict.get("falseNegativeRate")
        self.falsePositiveRate = test_config_dict.get("falsePositiveRate")

        # Metadata
        self.created_from = set(test_config_dict.get("created_from", []))
        self.created = datetime.fromisoformat(test_config_dict.get("created", datetime.now().isoformat()))
        self.last_run = datetime.fromisoformat(test_config_dict.get("last_run")) if test_config_dict.get("last_run") else None

    def __eq__(self, value):
        if not isinstance(value, TestConfig):
            return False
        return (self.name == value.name and
                self.n == value.n and
                self.k == value.k and
                self.distance_threshold == value.distance_threshold and
                self.unknown_psge_value == value.unknown_psge_value and
                self.min_confidence_threshold == value.min_confidence_threshold and
                self.max_error_threshold == value.max_error_threshold and
                self.init_p_e == value.init_p_e and
                self.bad_threshold == value.bad_threshold and
                self.damping_coeff == value.damping_coeff and
                self.init_observability == value.init_observability and
                self.observability_damping_coeff == value.observability_damping_coeff and
                self.sigmoid_midpoint == value.sigmoid_midpoint and
                self.sigmoid_steepness == value.sigmoid_steepness and
                self.falseNegativeRate == value.falseNegativeRate and
                self.falsePositiveRate == value.falsePositiveRate)
    
    def mogs(self, other) -> bool:
        if not isinstance(other, TestConfig):
            return False
        if self != other:
            return False
        for dataset in other.datasets:
            if dataset not in self.datasets:
                return False
        for mode in other.modes:
            if mode not in self.modes:
                return False
        if self.iterations < other.iterations:
            return False
        return True

    @staticmethod
    def LoadOrCreate(config_path: str) -> 'TestConfig':
        # If the file runtime_root/test_results/test_name/config.yaml does not exist, create it and return a new TestConfig
        new = TestConfig.from_file(config_path)
        if not new.configExists():
            new.createTestTree() # This will create the test tree and config file
            return new
        
        # Otherwise, we load the existing test config and see if it is mogged by the new one
        old = TestConfig.from_file(new.getConfigFilePath())
        if new.mogs(old):
            new.merge(old)
            new.createTestTree() # This will create any new test instances and update the config file
            return new
        else:
            raise ValueError("The new test configuration would invalidate the existing test configuration. Please resolve manually.")
    
    def merge(self, other: 'TestConfig') -> None:
        self.datasets.update(other.datasets)
        self.modes.update(other.modes)
        self.iterations = max(self.iterations, other.iterations)
        self.created = min(self.created, other.created)
        self.last_run = max(self.last_run, other.last_run) if other.last_run and self.last_run else self.last_run or other.last_run

    def configExists(self) -> bool:
        return os.path.exists(self.getConfigFilePath())

    def getTestRoot(self) -> str:
        return os.path.join(evm.getLatestResultsRoot(), to_filename(self.name))

    def getConfigFilePath(self) -> str:
        return os.path.join(self.getTestRoot(), "config.yaml")

    def createTestTree(self):
        os.makedirs(self.getTestRoot(), exist_ok=True)
        self.to_file(self.getConfigFilePath())
        for dataset in self.datasets:
            for mode in self.modes:
                for iteration in range(1, self.iterations + 1):
                    test_dir = os.path.join(self.getTestRoot(), dataset, mode, str(iteration))
                    if os.path.exists(os.path.join(test_dir, "instance.yaml")):
                        continue
                    os.makedirs(test_dir, exist_ok=True)
                    test_instance = TestInstance({
                        'version': evm.getLatestVersion()[0],
                        'name': self.name,
                        'dataset': dataset,
                        'mode': mode,
                        'iteration': iteration,

                        'n': self.n,
                        'k': self.k,
                        'distance_threshold': self.distance_threshold,
                        'unknown_psge_value': self.unknown_psge_value,
                        'min_confidence_threshold': self.min_confidence_threshold,
                        'max_error_threshold': self.max_error_threshold,
                        'init_p_e': self.init_p_e,
                        'bad_threshold': self.bad_threshold,
                        'damping_coeff': self.damping_coeff,
                        'init_observability': self.init_observability,
                        'observability_damping_coeff': self.observability_damping_coeff,
                        'sigmoid_midpoint': self.sigmoid_midpoint,
                        'sigmoid_steepness': self.sigmoid_steepness,
                        'falseNegativeRate': self.falseNegativeRate,
                        'falsePositiveRate': self.falsePositiveRate,
                    })
                    test_instance.to_file(os.path.join(test_dir, "instance.yaml"))

    @staticmethod
    def from_file(config_path: str) -> 'TestConfig':
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        config = TestConfig(config_dict)
        if config.size() == 0:
            raise ValueError("TestConfig must have at least one dataset, one mode, and one iteration.")
        return config
    
    def to_file(self, config_path: str) -> None:
        if not self.validate():
            print(f"TestConfig {self.name} is not valid and cannot be saved.")
        config_dict = {
            'name': self.name,
            'datasets': list(self.datasets),
            'modes': list(self.modes),
            'iterations': self.iterations,

            'n': self.n,
            'k': self.k,
            'distance_threshold': self.distance_threshold,
            'unknown_psge_value': self.unknown_psge_value,
            'min_confidence_threshold': self.min_confidence_threshold,
            'max_error_threshold': self.max_error_threshold,
            'init_p_e': self.init_p_e,
            'bad_threshold': self.bad_threshold,
            'damping_coeff': self.damping_coeff,
            'init_observability': self.init_observability,
            'observability_damping_coeff': self.observability_damping_coeff,
            'sigmoid_midpoint': self.sigmoid_midpoint,
            'sigmoid_steepness': self.sigmoid_steepness,
            'falseNegativeRate': self.falseNegativeRate,
            'falsePositiveRate': self.falsePositiveRate,

            'created': self.created.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
        }
        with open(config_path, 'w') as f:
            yaml.safe_dump(config_dict, f)

    def validate(self) -> bool:
        return (self.name is not None and
                len(self.datasets) > 0 and
                len(self.modes) > 0 and
                self.iterations > 0 and
                self.n is not None and
                self.k is not None and
                self.distance_threshold is not None and
                self.unknown_psge_value is not None and
                self.min_confidence_threshold is not None and
                self.max_error_threshold is not None and
                self.init_p_e is not None and
                self.bad_threshold is not None and
                self.damping_coeff is not None and
                self.init_observability is not None and
                self.observability_damping_coeff is not None and
                self.sigmoid_midpoint is not None and
                self.sigmoid_steepness is not None and
                self.falseNegativeRate is not None and
                self.falsePositiveRate is not None and
                self.created is not None and
                self.created_from is not None)
    
    def size(self) -> int:
        return len(self.datasets) * len(self.modes) * self.iterations
    
    def getUnrunTests(self, results_directory: str = '.') -> List[TestInstance]:
        unrun_tests = []
        for dataset in self.datasets:
            for mode in self.modes:
                for iteration in range(1, self.iterations + 1):
                    result_path = os.path.join(evm.getLatestResultsRoot(), to_filename(self.name), dataset, mode, str(iteration))
                    if not os.path.exists(os.path.join(results_directory, result_path)):
                        raise RuntimeError(f"Result path {result_path} does not exist.")
                    instance_path = os.path.join(result_path, "instance.yaml")
                    test_instance = TestInstance.from_file(instance_path)
                    if test_instance.status != "completed":
                        unrun_tests.append(test_instance)
        return unrun_tests
    
    def getUnevaluatedTests(self, results_directory: str = '.') -> List[TestInstance]:
        unevaluated_tests = []
        for dataset in self.datasets:
            for mode in self.modes:
                for iteration in range(1, self.iterations + 1):
                    result_path = os.path.join(evm.getLatestResultsRoot(), to_filename(self.name), dataset, mode, str(iteration))
                    if not os.path.exists(os.path.join(results_directory, result_path)):
                        raise RuntimeError(f"Result path {result_path} does not exist.")
                    instance_path = os.path.join(result_path, "instance.yaml")
                    test_instance = TestInstance.from_file(instance_path)
                    zip_files = [f for f in os.listdir(result_path) if f.endswith('.zip')]
                    if len(zip_files) != 4:
                        unevaluated_tests.append(test_instance)
        return unevaluated_tests
    
    def getAllTests(self, results_directory: str = '.') -> List[TestInstance]:
        all_tests = []
        for dataset in self.datasets:
            for mode in self.modes:
                for iteration in range(1, self.iterations + 1):
                    result_path = os.path.join(evm.getLatestResultsRoot(), to_filename(self.name), dataset, mode, str(iteration))
                    if not os.path.exists(os.path.join(results_directory, result_path)):
                        raise RuntimeError(f"Result path {result_path} does not exist.")
                    instance_path = os.path.join(result_path, "instance.yaml")
                    test_instance = TestInstance.from_file(instance_path)
                    all_tests.append(test_instance)
        return all_tests
    
    def __str__(self) -> str:
        return f"TestConfig(name={self.name}, datetime={self.datetime}, datasets={self.datasets}, modes={self.modes}, iterations={self.iterations})"
