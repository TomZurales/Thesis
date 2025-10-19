import subprocess

trajectories = [
    ("MH_01", "EuRoC.yaml"),
    ("MH_02", "EuRoC.yaml"),
    ("MH_03", "EuRoC.yaml"),
    ("MH_04", "EuRoC.yaml"),
    ("MH_05", "EuRoC.yaml"),
    ("V1_01", "EuRoC.yaml"),
    ("V1_02", "EuRoC.yaml"),
    ("V1_03", "EuRoC.yaml"),
    ("V2_01", "EuRoC.yaml"),
    ("V2_02", "EuRoC.yaml"),
    ("V2_03", "EuRoC.yaml"),
]

styles = [
    ("Baseline", ""),
    # ("VBEE", ""),
    # ("VBEE + RANSAC", "")
]

resultant_files = [
    "CameraTrajectory.txt",
    "KeyFrameTrajectory.txt",
]

subprocess.run(["mkdir", "-p", "results"])

for traj, settings in trajectories:
    for style, args in styles:
        print(f"Processing trajectory: {traj} {style}")
        subprocess.run(["mkdir", "-p", f"results/{traj}/{style.replace(' ', '_').replace('+', 'and')}"])
        subprocess.run(
            [
                "../slam_systems/ORB_SLAM3_Base/Examples/Stereo/stereo_euroc",
                "../slam_systems/ORB_SLAM3_Base/Vocabulary/ORBvoc.txt",
                f"../slam_systems/ORB_SLAM3_Base/Examples/Stereo/{settings}",
                f"../datasets/{traj}",
                f"../datasets/{traj}/timestamps.txt",
            ]
        )

        for file in resultant_files:
            subprocess.run(
                [
                    "mv",
                    file,
                    f"results/{traj}/{style.replace(' ', '_').replace('+', 'and')}/{file}",
                ]
            )
            subprocess.run(
                [
                    "evo_ape",
                    "euroc",
                    f"trajectories/ground_truths/{traj}/data.csv",
                    f"results/{traj}/{style.replace(' ', '_').replace('+', 'and')}/{file}",
                    "--align",
                    "--save_plot",
                    f"results/{traj}/{style.replace(' ', '_').replace('+', 'and')}/{file.replace('.txt', '') + '_ape'}",
                    "--save_results",
                    f"results/{traj}/{style.replace(' ', '_').replace('+', 'and')}/{file.replace('.txt', '') + '_ape'}.zip",
                ]
            )
            subprocess.run(
                [
                    "evo_rpe",
                    "euroc",
                    f"trajectories/ground_truths/{traj}/data.csv",
                    f"results/{traj}/{style.replace(' ', '_').replace('+', 'and')}/{file}",
                    "--align",
                    "--save_plot",
                    f"results/{traj}/{style.replace(' ', '_').replace('+', 'and')}/{file.replace('.txt', '') + '_rpe'}",
                    "--save_results",
                    f"results/{traj}/{style.replace(' ', '_').replace('+', 'and')}/{file.replace('.txt', '') + '_rpe'}.zip",
                ]
            )
