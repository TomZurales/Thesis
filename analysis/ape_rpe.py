import heapq
import os
from random import shuffle
import shutil
import subprocess
from multiprocessing import Pool
from average import TimedPose, average_poses

# The trajectories which will be tested
trajectories = [
    # ("all_machine_halls", "EuRoC.yaml"),
    # ("MH_02", "EuRoC.yaml"),
    # ("MH_03", "EuRoC.yaml"),
    # ("MH_04", "EuRoC.yaml"),
    # ("MH_05", "EuRoC.yaml"),
    # ("V1_01", "EuRoC.yaml"),
    # ("V1_02", "EuRoC.yaml"),
    # ("V1_03", "EuRoC.yaml"),
    # ("V2_01", "EuRoC.yaml"),
    # ("V2_02", "EuRoC.yaml"),
    # ("V2_03", "EuRoC.yaml"),
    # ("VBEE_LOW_HIGH", "VBEE.yaml"),
    # ("Checkerboard", "VBEE.yaml")
    ("big_skip", "VBEE.yaml")

]

# The run styles which will be tested
styles = [("Baseline", ""), ("VBEE", "vbee"), ("VBEE + RANSAC", "vbee ransac")]
# styles = [("VBEE", "vbee")]
# styles = [("Baseline", "")]

# The number of repetitions for each trajectory/style combination
reps = 1

# Ensure no results directory exists
subprocess.run(["rm", "-rf", "results"])

def run_and_evaluate(traj, settings, style, args, rep):
    subprocess.run(["mkdir", "-p", f"results/{traj}/{rep}"])
    print(
        f"Processing trajectory: {traj} {style.replace(' ', '_').replace('+', 'and')} Rep {rep}"
    )
    output_prefix = f"{traj}_{style.replace(' ', '_').replace('+', 'and')}_{rep}"
    output_dir = f"results/{traj}/{rep}"

    all_args = [
        "../slam_systems/ORB_SLAM3/Examples/Stereo/stereo_euroc",
        "../slam_systems/ORB_SLAM3/Vocabulary/ORBvoc.txt",
        f"../slam_systems/ORB_SLAM3/Examples/Stereo/{settings}",
        f"../datasets/{traj}",
        f"../datasets/{traj}/timestamps.txt",
        output_prefix,
    ]
    if args:
        all_args.extend(args.split(" "))
    print(" ".join(all_args))

    log_file = f"{output_dir}/{output_prefix}_log.txt"
    resultant_files = [
        f"{output_prefix}_Frame.txt",
        f"{output_prefix}_KeyFrame.txt",
        f"{output_prefix}_TrackedStats.csv",
    ]

    # Run ORB_SLAM until all resultant files exist
    completed = False
    while not completed:
        if os.path.exists(log_file):
            os.remove(log_file)
        for file in resultant_files:
            if os.path.exists(file):
                os.remove(file)
        with open(log_file, "w") as f:
            f.write(" ".join(all_args) + "\n")
            try:
                subprocess.run(all_args, stdout=f, stderr=f, timeout=1800)
                f.flush()
                completed = all(os.path.exists(file) for file in resultant_files)
            except subprocess.TimeoutExpired:
                print("Run timed out, restarting...")
                f.write("Run timed out\n")
        # with open(log_file, "r") as log_read:
        #     if "Fail to track local map!" in log_read.read():
        #         completed = False

    for file in resultant_files:
        # Move resultant file into the results directory
        subprocess.run(
            [
                "mv",
                file,
                output_dir,
            ]
        )

        # Get the ground truth for this trajectory
        groundtruth_path = f"../datasets/{traj}/mav0/state_groundtruth_estimate0/data.tum"
        
        # Evaluate APE and RPE using evo
        subprocess.run(
            [
                "evo_ape",
                "tum",
                groundtruth_path,
                f"{output_dir}/{file}",
                "--align",
                "-s",
                "--save_plot",
                f"{output_dir}/{file.replace('.txt', '') + '_ape'}",
                "--save_results",
                f"{output_dir}/{file.replace('.txt', '') + '_ape'}.zip",
            ]
        )
        subprocess.run(
            [
                "evo_rpe",
                "tum",
                groundtruth_path,
                f"{output_dir}/{file}",
                "--align",
                "-s",
                "--save_plot",
                f"{output_dir}/{file.replace('.txt', '') + '_rpe'}",
                "--save_results",
                f"{output_dir}/{file.replace('.txt', '') + '_rpe'}.zip",
            ]
        )


arg_list = []

for traj, settings in trajectories:
    for style, args in styles:
        for rep in range(1, reps + 1):
            arg_list.append((traj, settings, style, args, rep))
shuffle(arg_list)
with Pool(10) as p:
    p.starmap(run_and_evaluate, arg_list)

# # After all runs are complete, average the results
# result_types = ["Frame", "KeyFrame"]
# for trajectory, _ in trajectories:
#     trajectory_dir = os.path.join("results", trajectory)
#     iterations = [d for d in os.listdir(trajectory_dir) if os.path.isdir(os.path.join(trajectory_dir, d)) and d != "average"]

#     if os.path.exists(os.path.join(trajectory_dir, "average")):
#         shutil.rmtree(os.path.join(trajectory_dir, "average"))
#     os.mkdir(os.path.join(trajectory_dir, "average"))
#     average_dir = os.path.join(trajectory_dir, "average")

#     for run_type, _ in styles:
#         for result_type in result_types:
#             all_poses = []
#             min_ts = float('inf')
#             max_ts = float('-inf')
#             for iteration in iterations:
#                 with open(os.path.join(trajectory_dir, iteration, f"{trajectory}_{run_type.replace(' ', '_').replace('+', 'and')}_{iteration}_{result_type}.txt"), 'r') as f:
#                     for line in f:
#                         tp = TimedPose.from_string(line.strip())
#                         if tp.timestamp < min_ts:
#                             min_ts = tp.timestamp
#                         if tp.timestamp > max_ts:
#                             max_ts = tp.timestamp
#                         all_poses.append(tp)
#             all_poses_heap = heapq.heapify(all_poses)
#             average_num_poses = len(all_poses) / len(iterations)
#             averaged_poses = []
#             ts_increment = (max_ts - min_ts) / average_num_poses
#             cur_ts = min_ts + ts_increment
#             to_average = []

#             while all_poses:
#                 pose = heapq.heappop(all_poses)
#                 if pose.timestamp <= cur_ts:
#                     to_average.append(pose)
#                 else:
#                     if to_average:
#                         averaged_pose = average_poses(to_average)
#                         averaged_poses.append(averaged_pose)
#                         to_average = [pose]
#                     cur_ts += ts_increment
#             if to_average:
#                 averaged_pose = average_poses(to_average)
#                 averaged_poses.append(averaged_pose)

#             with open(os.path.join(average_dir, f"{trajectory}_{run_type.replace(' ', '_').replace('+', 'and')}_average_{result_type}.txt"), 'w') as f:
#                 for pose in averaged_poses:
#                     f.write(f"{pose}\n")

#                 # Evaluate APE and RPE using evo
#                 subprocess.run(
#                     [
#                         "evo_ape",
#                         "tum",
#                         f"trajectories/ground_truths/{trajectory}/data.tum",
#                         os.path.join(average_dir, f"{trajectory}_{run_type.replace(' ', '_').replace('+', 'and')}_average_{result_type}.txt"),
#                         "--align",
#                         "-s",
#                         "--save_plot",
#                         os.path.join(average_dir, f"{trajectory}_{run_type.replace(' ', '_').replace('+', 'and')}_average_{result_type}_ape"),
#                         "--save_results",
#                         os.path.join(average_dir, f"{trajectory}_{run_type.replace(' ', '_').replace('+', 'and')}_average_{result_type}_ape.zip"),
#                     ]
#                 )
#                 subprocess.run(
#                     [
#                         "evo_rpe",
#                         "tum",
#                         f"trajectories/ground_truths/{trajectory}/data.tum",
#                         os.path.join(average_dir, f"{trajectory}_{run_type.replace(' ', '_').replace('+', 'and')}_average_{result_type}.txt"),
#                         "--align",
#                         "-s",
#                         "--save_plot",
#                         os.path.join(average_dir, f"{trajectory}_{run_type.replace(' ', '_').replace('+', 'and')}_average_{result_type}_rpe"),
#                         "--save_results",
#                         os.path.join(average_dir, f"{trajectory}_{run_type.replace(' ', '_').replace('+', 'and')}_average_{result_type}_rpe.zip"),
#                     ]
#                 )