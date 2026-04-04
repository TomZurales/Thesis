import string
from typing import Dict, List, Literal, Tuple
from libtest_runner import TestConfig, TestInstance
import subprocess
import os
import random
import pprint

runtime_root = os.getenv("THESIS_RUNTIME_ROOT")
thesis_root = os.getenv("THESIS_ROOT")

if not runtime_root:
    raise RuntimeError("THESIS_RUNTIME_ROOT environment variable not set")

if not thesis_root:
    raise RuntimeError("THESIS_ROOT environment variable not set")


def generate_evo_stats(test: TestInstance):
    if test.status != "completed":
        raise RuntimeError("Test must be completed to evaluate trajectories")
    success = False
    try:
        subprocess.run(
            [
                "evo_ape",
                "tum",
                os.path.join(
                    thesis_root,
                    "datasets",
                    test.dataset,
                    "mav0",
                    "state_groundtruth_estimate0",
                    "data.tum",
                ),
                "CameraTrajectory.txt",
                "--align",
                "-s",
                "--save_results",
                "ape_camera.zip",
            ],
            timeout=30,
            cwd=test.getCwd(),
        )

        subprocess.run(
            [
                "evo_ape",
                "tum",
                os.path.join(
                    thesis_root,
                    "datasets",
                    test.dataset,
                    "mav0",
                    "state_groundtruth_estimate0",
                    "data.tum",
                ),
                "KeyFrameTrajectory.txt",
                "--align",
                "-s",
                "--save_results",
                "ape_keyframe.zip",
            ],
            timeout=30,
            cwd=test.getCwd(),
        )

        subprocess.run(
            [
                "evo_rpe",
                "tum",
                os.path.join(
                    thesis_root,
                    "datasets",
                    test.dataset,
                    "mav0",
                    "state_groundtruth_estimate0",
                    "data.tum",
                ),
                "CameraTrajectory.txt",
                "--align",
                "-s",
                "--save_results",
                "rpe_camera.zip",
            ],
            timeout=30,
            cwd=test.getCwd(),
        )

        subprocess.run(
            [
                "evo_rpe",
                "tum",
                os.path.join(
                    thesis_root,
                    "datasets",
                    test.dataset,
                    "mav0",
                    "state_groundtruth_estimate0",
                    "data.tum",
                ),
                "KeyFrameTrajectory.txt",
                "--align",
                "-s",
                "--save_results",
                "rpe_keyframe.zip",
            ],
            timeout=30,
            cwd=test.getCwd(),
        )
        success = True
    except Exception as e:
        print("Error generating evo stats for test:", test, "Error:", e)

    return success


def hasEvoRun(test: TestInstance) -> bool:
    cwd = test.getCwd()
    required_files = [
        "ape_camera.zip",
        "ape_keyframe.zip",
        "rpe_camera.zip",
        "rpe_keyframe.zip",
    ]
    for f in required_files:
        if not os.path.isfile(os.path.join(cwd, f)):
            return False
    return True


def csvs_exist(test: TestInstance) -> bool:
    cwd = test.getCwd()
    required_files = [
        "ape_camera.csv",
        "ape_keyframe.csv",
        "rpe_camera.csv",
        "rpe_keyframe.csv",
    ]
    for f in required_files:
        if not os.path.isfile(os.path.join(cwd, f)):
            return False
    return True


def add_test_info_to_csv(
    test: TestInstance,
    csv_file: str,
    include_iteration: bool = True,
    include_dataset: bool = True,
):
    with open(csv_file, "r") as f:
        lines = f.readlines()
    with open(csv_file, "w") as f:
        if include_iteration and include_dataset:
            f.write("name,dataset,mode,iteration,rmse,mean,median,std,min,max,sse\n")
        elif include_iteration:
            f.write("name,mode,iteration,rmse,mean,median,std,min,max,sse\n")
        elif include_dataset:
            f.write("name,dataset,mode,rmse,mean,median,std,min,max,sse\n")
        else:
            f.write("name,mode,rmse,mean,median,std,min,max,sse\n")
        for line in lines:
            if include_iteration and include_dataset:
                f.write(
                    f"{test.name},{test.dataset},{test.mode},{test.iteration},{','.join(line.split(',')[1:])}"
                )
            elif include_iteration:
                f.write(
                    f"{test.name},{test.mode},{test.iteration},{','.join(line.split(',')[1:])}"
                )
            elif include_dataset:
                f.write(
                    f"{test.name},{test.dataset},{test.mode},{','.join(line.split(',')[1:])}"
                )
            else:
                f.write(f"{test.name},{test.mode},{','.join(line.split(',')[1:])}")


def combine_csvs(csv_files: List[str], output_file: str):
    with open(output_file, "w") as outfile:
        header_written = False
        for csv_file in csv_files:
            with open(csv_file, "r") as infile:
                lines = infile.readlines()
                if not header_written:
                    outfile.write(lines[0])
                    header_written = True
                for line in lines[1:]:
                    outfile.write(line)


def get_evo_data(test: TestInstance) -> List[List[str]]:
    if not os.path.isfile(os.path.join(test.getCwd(), "ape_camera.csv")):
        subprocess.run(
            [
                "evo_res",
                os.path.join(test.getCwd(), "ape_camera.zip"),
                "--save_table",
                "ape_camera.csv",
            ],
            timeout=30,
            cwd=test.getCwd(),
        )
    camera_ape = [test.name, test.dataset, test.mode, str(test.iteration)]
    with open(os.path.join(test.getCwd(), "ape_camera.csv"), "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            raise RuntimeError("Unexpected number of lines in evo csv output: ", test.name, test.dataset, test.mode, test.iteration)
        values = lines[1].strip().split(",")[1:]
        camera_ape.extend(values)

    if not os.path.isfile(os.path.join(test.getCwd(), "ape_keyframe.csv")):
        subprocess.run(
            [
                "evo_res",
                os.path.join(test.getCwd(), "ape_keyframe.zip"),
                "--save_table",
                "ape_keyframe.csv",
            ],
            timeout=30,
            cwd=test.getCwd(),
        )
    keyframe_ape = [test.name, test.dataset, test.mode, str(test.iteration)]
    with open(os.path.join(test.getCwd(), "ape_keyframe.csv"), "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            raise RuntimeError("Unexpected number of lines in evo csv output: ", test.name, test.dataset, test.mode, test.iteration)
        values = lines[1].strip().split(",")[1:]
        keyframe_ape.extend(values)

    if not os.path.isfile(os.path.join(test.getCwd(), "rpe_camera.csv")):
        subprocess.run(
            [
                "evo_res",
                os.path.join(test.getCwd(), "rpe_camera.zip"),
                "--save_table",
                "rpe_camera.csv",
            ],
            timeout=30,
            cwd=test.getCwd(),
        )
    camera_rpe = [test.name, test.dataset, test.mode, str(test.iteration)]
    with open(os.path.join(test.getCwd(), "rpe_camera.csv"), "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            raise RuntimeError("Unexpected number of lines in evo csv output: ", test.name, test.dataset, test.mode, test.iteration)
        values = lines[1].strip().split(",")[1:]
        camera_rpe.extend(values)

    if not os.path.isfile(os.path.join(test.getCwd(), "rpe_keyframe.csv")):
        subprocess.run(
            [
                "evo_res",
                os.path.join(test.getCwd(), "rpe_keyframe.zip"),
                "--save_table",
                "rpe_keyframe.csv",
            ],
            timeout=30,
            cwd=test.getCwd(),
        )
    keyframe_rpe = [test.name, test.dataset, test.mode, str(test.iteration)]
    with open(os.path.join(test.getCwd(), "rpe_keyframe.csv"), "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            raise RuntimeError("Unexpected number of lines in evo csv output: ", test.name, test.dataset, test.mode, test.iteration)
        values = lines[1].strip().split(",")[1:]
        keyframe_rpe.extend(values)

    return [camera_ape, keyframe_ape, camera_rpe, keyframe_rpe]

def get_random_filename(length: int = 15) -> str:
    characters = string.ascii_letters + string.digits 
    random_string = ''.join(random.choices(characters, k=length))
    return random_string + ".csv"

def get_evo_data_by_mode(tests_by_mode: Dict[str, List[TestInstance]]) -> List[List[List[str]]]:
    tmpdir = os.path.join(runtime_root, ".tmp")
    os.makedirs(tmpdir, exist_ok=True)

    results = []
    results.append([])
    results.append([])
    results.append([])
    results.append([])

    for mode, tests in tests_by_mode.items():
        camera_ape_tmpfile = os.path.join(tmpdir, get_random_filename())
        subprocess.run(
            ["evo_res", "--merge"]
            + [os.path.join(test.getCwd(), "ape_camera.zip") for test in tests]
            + ["--save_table", camera_ape_tmpfile],
            timeout=30
        )
        camera_ape = [tests[0].name, mode]
        with open(camera_ape_tmpfile, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise RuntimeError("Unexpected number of lines in evo csv output for mode: ", mode)
            values = lines[1].strip().split(",")[1:]
            camera_ape.extend(values)
        results[0].append(camera_ape)

        keyframe_ape_tmpfile = os.path.join(tmpdir, get_random_filename())
        subprocess.run(
            ["evo_res", "--merge"]
            + [os.path.join(test.getCwd(), "ape_keyframe.zip") for test in tests]
            + ["--save_table", keyframe_ape_tmpfile],
            timeout=30
        )
        keyframe_ape = [tests[0].name, mode]
        with open(keyframe_ape_tmpfile, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise RuntimeError("Unexpected number of lines in evo csv output for mode: ", mode)
            values = lines[1].strip().split(",")[1:]
            keyframe_ape.extend(values)
        results[1].append(keyframe_ape)

        camera_rpe_tmpfile = os.path.join(tmpdir, get_random_filename())
        subprocess.run(
            ["evo_res", "--merge"]
            + [os.path.join(test.getCwd(), "rpe_camera.zip") for test in tests]
            + ["--save_table", camera_rpe_tmpfile],
            timeout=30
        )
        camera_rpe = [tests[0].name, mode]
        with open(camera_rpe_tmpfile, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise RuntimeError("Unexpected number of lines in evo csv output for mode: ", mode)
            values = lines[1].strip().split(",")[1:]
            camera_rpe.extend(values)
        results[2].append(camera_rpe)
        
        keyframe_rpe_tmpfile = os.path.join(tmpdir, get_random_filename())
        subprocess.run(
            ["evo_res", "--merge"]
            + [os.path.join(test.getCwd(), "rpe_keyframe.zip") for test in tests]
            + ["--save_table", keyframe_rpe_tmpfile],
            timeout=30
        )
        keyframe_rpe = [tests[0].name, mode]
        with open(keyframe_rpe_tmpfile, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise RuntimeError("Unexpected number of lines in evo csv output for mode: ", mode)
            values = lines[1].strip().split(",")[1:]
            keyframe_rpe.extend(values)
        results[3].append(keyframe_rpe)

    return results

def get_evo_data_by_mode_and_dataset(tests_by_mode_and_dataset: Dict[Tuple[str, str], List[TestInstance]]) -> List[List[List[str]]]:
    tmpdir = os.path.join(runtime_root, ".tmp")
    os.makedirs(tmpdir, exist_ok=True)

    results = []
    results.append([])
    results.append([])
    results.append([])
    results.append([])

    for key, tests in tests_by_mode_and_dataset.items():
        camera_ape_tmpfile = os.path.join(tmpdir, get_random_filename())
        subprocess.run(
            ["evo_res", "--merge"]
            + [os.path.join(test.getCwd(), "ape_camera.zip") for test in tests]
            + ["--save_table", camera_ape_tmpfile],
            timeout=30
        )
        camera_ape = [tests[0].name, key[0], key[1]]
        with open(camera_ape_tmpfile, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise RuntimeError("Unexpected number of lines in evo csv output for mode: ", key)
            values = lines[1].strip().split(",")[1:]
            camera_ape.extend(values)
        results[0].append(camera_ape)

        keyframe_ape_tmpfile = os.path.join(tmpdir, get_random_filename())
        subprocess.run(
            ["evo_res", "--merge"]
            + [os.path.join(test.getCwd(), "ape_keyframe.zip") for test in tests]
            + ["--save_table", keyframe_ape_tmpfile],
            timeout=30
        )
        keyframe_ape = [tests[0].name, key[0], key[1]]
        with open(keyframe_ape_tmpfile, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise RuntimeError("Unexpected number of lines in evo csv output for mode: ", key)
            values = lines[1].strip().split(",")[1:]
            keyframe_ape.extend(values)
        results[1].append(keyframe_ape)

        camera_rpe_tmpfile = os.path.join(tmpdir, get_random_filename())
        subprocess.run(
            ["evo_res", "--merge"]
            + [os.path.join(test.getCwd(), "rpe_camera.zip") for test in tests]
            + ["--save_table", camera_rpe_tmpfile],
            timeout=30
        )
        camera_rpe = [tests[0].name, key[0], key[1]]
        with open(camera_rpe_tmpfile, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise RuntimeError("Unexpected number of lines in evo csv output for mode: ", key)
            values = lines[1].strip().split(",")[1:]
            camera_rpe.extend(values)
        results[2].append(camera_rpe)
        
        keyframe_rpe_tmpfile = os.path.join(tmpdir, get_random_filename())
        subprocess.run(
            ["evo_res", "--merge"]
            + [os.path.join(test.getCwd(), "rpe_keyframe.zip") for test in tests]
            + ["--save_table", keyframe_rpe_tmpfile],
            timeout=30
        )
        keyframe_rpe = [tests[0].name, key[0], key[1]]
        with open(keyframe_rpe_tmpfile, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise RuntimeError("Unexpected number of lines in evo csv output for mode: ", key)
            values = lines[1].strip().split(",")[1:]
            keyframe_rpe.extend(values)
        results[3].append(keyframe_rpe)

    return results

def write_list_to_csv(data: List[List[str]], output_file: str):
    with open(output_file, "w") as f:
        for row in data:
            print(row)
            f.write(",".join(row) + "\n")

def generate_csvs(test_set: TestConfig):
    all_tests = test_set.getAllTests()

    to_merge_by_mode: Dict[str, List[TestInstance]] = {}
    to_merge_by_mode_and_dataset: Dict[Tuple[str, str], List[TestInstance]] = {}

    camera_ape_all = [
        [
            "name",
            "dataset",
            "mode",
            "iteration",
            "rmse",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "sse",
        ]
    ]
    keyframe_ape_all = [
        [
            "name",
            "dataset",
            "mode",
            "iteration",
            "rmse",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "sse",
        ]
    ]
    camera_rpe_all = [
        [
            "name",
            "dataset",
            "mode",
            "iteration",
            "rmse",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "sse",
        ]
    ]
    keyframe_rpe_all = [
        [
            "name",
            "dataset",
            "mode",
            "iteration",
            "rmse",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "sse",
        ]
    ]
    camera_ape_by_mode = [
        ["name", "mode", "rmse", "mean", "median", "std", "min", "max", "sse"]
    ]
    keyframe_ape_by_mode = [
        ["name", "mode", "rmse", "mean", "median", "std", "min", "max", "sse"]
    ]
    camera_rpe_by_mode = [
        ["name", "mode", "rmse", "mean", "median", "std", "min", "max", "sse"]
    ]
    keyframe_rpe_by_mode = [
        ["name", "mode", "rmse", "mean", "median", "std", "min", "max", "sse"]
    ]
    camera_ape_by_mode_and_dataset = [
        [
            "name",
            "mode",
            "dataset",
            "rmse",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "sse",
        ]
    ]
    keyframe_ape_by_mode_and_dataset = [
        [
            "name",
            "mode",
            "dataset",
            "rmse",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "sse",
        ]
    ]
    camera_rpe_by_mode_and_dataset = [
        [
            "name",
            "mode",
            "dataset",
            "rmse",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "sse",
        ]
    ]
    keyframe_rpe_by_mode_and_dataset = [
        [
            "name",
            "mode",
            "dataset",
            "rmse",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "sse",
        ]
    ]

    for test in all_tests:
        if not hasEvoRun(test):
            raise RuntimeError("EVO has not been run for this test")

        # Generate merge lists to run through evo again later
        if test.mode not in to_merge_by_mode:
            to_merge_by_mode[test.mode] = []
        to_merge_by_mode[test.mode].append(test)
        key = (test.mode, test.dataset)
        if key not in to_merge_by_mode_and_dataset:
            to_merge_by_mode_and_dataset[key] = []
        to_merge_by_mode_and_dataset[key].append(test)

        lines = get_evo_data(test)
        camera_ape_all.append(lines[0])
        keyframe_ape_all.append(lines[1])
        camera_rpe_all.append(lines[2])
        keyframe_rpe_all.append(lines[3])

    write_list_to_csv(camera_ape_all, os.path.join(test_set.getTestRoot(), "ape_camera_all.csv"))
    write_list_to_csv(keyframe_ape_all, os.path.join(test_set.getTestRoot(), "ape_keyframe_all.csv"))
    write_list_to_csv(camera_rpe_all, os.path.join(test_set.getTestRoot(), "rpe_camera_all.csv"))
    write_list_to_csv(keyframe_rpe_all, os.path.join(test_set.getTestRoot(), "rpe_keyframe_all.csv"))

    by_mode = get_evo_data_by_mode(to_merge_by_mode)
    
    camera_ape_by_mode.extend(by_mode[0])
    keyframe_ape_by_mode.extend(by_mode[1])
    camera_rpe_by_mode.extend(by_mode[2])
    keyframe_rpe_by_mode.extend(by_mode[3])

    write_list_to_csv(camera_ape_by_mode, os.path.join(test_set.getTestRoot(), "ape_camera_by_mode.csv"))
    write_list_to_csv(keyframe_ape_by_mode, os.path.join(test_set.getTestRoot(), "ape_keyframe_by_mode.csv"))
    write_list_to_csv(camera_rpe_by_mode, os.path.join(test_set.getTestRoot(), "rpe_camera_by_mode.csv"))
    write_list_to_csv(keyframe_rpe_by_mode, os.path.join(test_set.getTestRoot(), "rpe_keyframe_by_mode.csv"))

    by_mode_and_dataset = get_evo_data_by_mode_and_dataset(to_merge_by_mode_and_dataset)
    
    camera_ape_by_mode_and_dataset.extend(by_mode_and_dataset[0])
    keyframe_ape_by_mode_and_dataset.extend(by_mode_and_dataset[1])
    camera_rpe_by_mode_and_dataset.extend(by_mode_and_dataset[2])
    keyframe_rpe_by_mode_and_dataset.extend(by_mode_and_dataset[3])

    write_list_to_csv(camera_ape_by_mode_and_dataset, os.path.join(test_set.getTestRoot(), "ape_camera_by_mode_and_dataset.csv"))
    write_list_to_csv(keyframe_ape_by_mode_and_dataset, os.path.join(test_set.getTestRoot(), "ape_keyframe_by_mode_and_dataset.csv"))
    write_list_to_csv(camera_rpe_by_mode_and_dataset, os.path.join(test_set.getTestRoot(), "rpe_camera_by_mode_and_dataset.csv"))
    write_list_to_csv(keyframe_rpe_by_mode_and_dataset, os.path.join(test_set.getTestRoot(), "rpe_keyframe_by_mode_and_dataset.csv"))

    return [
        os.path.join(test.getCwd(), f)
        for f in [
            "ape_camera.csv",
            "ape_keyframe.csv",
            "rpe_camera.csv",
            "rpe_keyframe.csv",
        ]
    ]


def evo_merge_to_csv(test_set: TestConfig, tests: List[TestInstance], suffix: str):
    # if not hasEvoRun(tests):
    #     raise RuntimeError("EVO has not been run for this test")

    subprocess.run(
        ["evo_res", "--merge"]
        + [os.path.join(test.getCwd(), "ape_camera.zip") for test in tests]
        + ["--save_table", f"ape_camera_{suffix}.csv"],
        timeout=30,
        cwd=test_set.getTestRoot(),
    )

    subprocess.run(
        ["evo_res", "--merge"]
        + [os.path.join(test.getCwd(), "ape_keyframe.zip") for test in tests]
        + ["--save_table", f"ape_keyframe_{suffix}.csv"],
        timeout=30,
        cwd=os.path.join(tests[0].getCwd(), "..", "..", ".."),
    )

    subprocess.run(
        [
            "evo_res",
            "--merge",
        ]
        + [os.path.join(test.getCwd(), "rpe_camera.zip") for test in tests]
        + ["--save_table", f"rpe_camera_{suffix}.csv"],
        timeout=30,
        cwd=os.path.join(tests[0].getCwd(), "..", "..", ".."),
    )

    subprocess.run(
        ["evo_res", "--merge"]
        + [os.path.join(test.getCwd(), "rpe_keyframe.zip") for test in tests]
        + ["--save_table", f"rpe_keyframe_{suffix}.csv"],
        timeout=30,
        cwd=os.path.join(tests[0].getCwd(), "..", "..", ".."),
    )

    return [
        os.path.join(os.path.join(tests[0].getCwd(), "..", "..", ".."), f)
        for f in [
            f"ape_camera_{suffix}.csv",
            f"ape_keyframe_{suffix}.csv",
            f"rpe_camera_{suffix}.csv",
            f"rpe_keyframe_{suffix}.csv",
        ]
    ]


def aggregateEvoStats(test_set: TestConfig):
    generate_csvs(test_set)
    return
    all_tests = test_set.getAllTests()

    by_mode_and_dataset = {}
    by_mode = {}

    for test in all_tests:
        if test.mode not in by_mode:
            by_mode[test.mode] = []
        by_mode[test.mode].append(test)

        key = (test.mode, test.dataset)
        if key not in by_mode_and_dataset:
            by_mode_and_dataset[key] = []
        by_mode_and_dataset[key].append(test)

    for key, tests in by_mode_and_dataset.items():
        files = evo_merge_to_csv(tests, suffix=f"{key[0]}_{key[1]}")
        print(f"Aggregated EVO stats for mode {key[0]} and dataset {key[1]}:")
        print("APE Camera:", files[0])
        print("APE Keyframe:", files[1])
        print("RPE Camera:", files[2])
        print("RPE Keyframe:", files[3])

    for mode, tests in by_mode.items():
        files = evo_merge_to_csv(tests, suffix=f"{mode}")
        print(f"Aggregated EVO stats for mode {mode}:")
        print("APE Camera:", files[0])
        print("APE Keyframe:", files[1])
        print("RPE Camera:", files[2])
        print("RPE Keyframe:", files[3])

    with open(
        os.path.join(test_set.getTestRoot(), "ape_camera_all.csv"), "w"
    ) as ape_camera_all_file, open(
        os.path.join(test_set.getTestRoot(), "ape_keyframe_all.csv"), "w"
    ) as ape_keyframe_all_file, open(
        os.path.join(test_set.getTestRoot(), "rpe_camera_all.csv"), "w"
    ) as rpe_camera_all_file, open(
        os.path.join(test_set.getTestRoot(), "rpe_keyframe_all.csv"), "w"
    ) as rpe_keyframe_all_file:
        ape_camera_all_file.write(
            "name,dataset,mode,iteration,rmse,mean,median,std,min,max,sse\n"
        )
        ape_camera_all_file.write(
            "name,dataset,mode,iteration,rmse,mean,median,std,min,max,sse\n"
        )
        ape_keyframe_all_file.write(
            "name,dataset,mode,iteration,rmse,mean,median,std,min,max,sse\n"
        )
        rpe_camera_all_file.write(
            "name,dataset,mode,iteration,rmse,mean,median,std,min,max,sse\n"
        )
        rpe_keyframe_all_file.write(
            "name,dataset,mode,iteration,rmse,mean,median,std,min,max,sse\n"
        )
        for test in all_tests:
            files = evo_to_csv(test)
            with open(files[0], "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    ape_camera_all_file.write(
                        f"{test.name},{test.dataset},{test.mode},{test.iteration},{','.join(line.split(',', 1)[1:])}"
                    )

            with open(files[1], "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    ape_keyframe_all_file.write(
                        f"{test.name},{test.dataset},{test.mode},{test.iteration},{','.join(line.split(',', 1)[1:])}"
                    )

            with open(files[2], "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    rpe_camera_all_file.write(
                        f"{test.name},{test.dataset},{test.mode},{test.iteration},{','.join(line.split(',', 1)[1:])}"
                    )

            with open(files[3], "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    rpe_keyframe_all_file.write(
                        f"{test.name},{test.dataset},{test.mode},{test.iteration},{','.join(line.split(',', 1)[1:])}"
                    )

    print("Aggregated EVO stats for test set:", test_set.name)
