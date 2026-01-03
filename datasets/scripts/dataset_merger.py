import os
import shutil
from pathlib import Path
from typing import Tuple, List
import sys

def read_timestamps(timestamps_file: str) -> List[int]:
    """Read timestamps from a timestamps.txt file.
    
    Returns a list of timestamps.
    """
    timestamps = []
    with open(timestamps_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                timestamps.append(int(line))
    return timestamps

def offset_timestamps(timestamps: List[int], offset: int) -> List[int]:
    """Offset all timestamps by a given amount."""
    return [ts + offset for ts in timestamps]

def read_ground_truth(dataset_path: str) -> List[float]:
    gt_file = dataset_path / 'mav0' / 'state_groundtruth_estimate0' / 'data.csv'
    tum_mode = False
    if not gt_file.exists():
        gt_file = dataset_path / 'mav0' / 'state_groundtruth_estimate0' / 'data.tum'
        if not gt_file.exists():
            raise FileNotFoundError(f"Ground truth file not found in {dataset_path}")
        tum_mode = True
    
    ground_truth = []
    with open(gt_file, 'r') as f:
        for line in f:
            if '#' in line:
                continue
            line = line.strip()
            if line:
                if tum_mode:
                    parts = line.split()
                    timestamp = float(parts[0])
                    pose = [float(parts[1]), float(parts[2]), float(parts[3]),
                            float(parts[4]), float(parts[5]), float(parts[6]), float(parts[7])]
                    ground_truth.append([timestamp] + pose)
                else:
                    parts = line.split(',')
                    timestamp = float(parts[0]) / 1e9
                    pose = [float(parts[1]), float(parts[2]), float(parts[3]),
                            float(parts[5]), float(parts[6]), float(parts[7]), float(parts[4])]
                    ground_truth.append([timestamp] + pose)
    return ground_truth

def offset_ground_truth(ground_truth: List[float], offset: float) -> List[float]:
    """Offset all ground truth timestamps by a given amount."""
    return [[gt[0] + offset] + gt[1:] for gt in ground_truth]

def write_ground_truth(gt_file: str, ground_truth: List[float]) -> None:
    with open(gt_file, 'w') as f:
        for gt in ground_truth:
            line = " ".join(str(val) for val in gt) + "\n"
            f.write(line)

def merge_datasets(dataset1_path: str, dataset2_path: str, output_path: str) -> None:
    """Merge two EuRoC style datasets.
    
    Args:
        dataset1_path: Path to first dataset
        dataset2_path: Path to second dataset
        output_path: Path for merged dataset
    """
    dataset1_path = Path(dataset1_path)
    dataset2_path = Path(dataset2_path)
    output_path = Path(output_path)
    
    # Create output directory structure
    if output_path == dataset1_path:
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path.mkdir(parents=True, exist_ok=False)
    
    # Define camera directories (stereo: left and right)
    cameras = ['mav0/cam0', 'mav0/cam1']
    
    # Read timestamps from both datasets
    timestamps1 = read_timestamps(dataset1_path / 'timestamps.txt')
    timestamps2 = read_timestamps(dataset2_path / 'timestamps.txt')
    
    if not timestamps1:
        raise ValueError("Dataset 1 has no timestamps")
    if not timestamps2:
        raise ValueError("Dataset 2 has no timestamps")
    
    # Calculate offset: dataset2 starts at the end of dataset1
    max_timestamp_dataset1 = max(timestamps1)
    min_timestamp_dataset2 = min(timestamps2)
    offset = max_timestamp_dataset1 - min_timestamp_dataset2
    offset += timestamps2[1] - timestamps2[0]
        
    (output_path / 'mav0' / 'state_groundtruth_estimate0').mkdir(parents=True, exist_ok=True)
    gt1 = read_ground_truth(dataset1_path)
    gt2 = read_ground_truth(dataset2_path)
    gt2_offset = offset_ground_truth(gt2, offset / 1e9)
    merged_gt = gt1 + gt2_offset
    merged_gt.sort(key=lambda x: x[0])
    write_ground_truth(output_path / 'mav0' / 'state_groundtruth_estimate0' / 'data.tum', merged_gt)

    ds1_filenames = [str(ts) + '.png' for ts in timestamps1]
    
    # Offset dataset2 timestamps
    timestamps2_offset = offset_timestamps(timestamps2, offset)
    old_filenames = [str(ts) + '.png' for ts in timestamps2]
    new_filenames = [str(ts) + '.png' for ts in timestamps2_offset]
    timestamps2_offset.sort()

    with open(output_path / 'splits.txt', 'a') as f:
        f.write(f"{timestamps2_offset[0]}\n")

    # Merge timestamps
    merged_timestamps = timestamps1 + timestamps2_offset
    merged_timestamps.sort()
    
    # Copy stereo images
    for camera in cameras:
        cam_src1 = dataset1_path / camera / 'data'
        cam_src2 = dataset2_path / camera / 'data'
        cam_dst = output_path / camera / 'data'
        
        cam_dst.mkdir(parents=True, exist_ok=True)
        
        # Copy images from dataset1
        if output_path != dataset1_path:
            if cam_src1.exists():
                for i in range(len(timestamps1)):
                    shutil.copy2(cam_src1 / ds1_filenames[i], cam_dst / ds1_filenames[i])
        
        # Copy images from dataset2
        if cam_src2.exists():
            for i in range(len(old_filenames)):
                shutil.copy2(cam_src2 / old_filenames[i], cam_dst / new_filenames[i])
    
    # Write merged timestamps
    with open(output_path / 'timestamps.txt', 'w') as f:
        for timestamp in merged_timestamps:
            f.write(f"{timestamp}\n")
    
    print(f"Datasets merged successfully!")
    print(f"Dataset 1: {len(timestamps1)} frames")
    print(f"Dataset 2: {len(timestamps2)} frames")
    print(f"Merged: {len(merged_timestamps)} frames")
    print(f"Timestamp offset applied to dataset 2: {offset:.6f}")
    print(f"Output directory: {output_path}")

if __name__ == "__main__":
    # Example usage

    n_sets_to_merge = len(sys.argv) - 2
    input_sets = sys.argv[1:-1]
    output = sys.argv[-1]

    for i in range(n_sets_to_merge - 1):
        dataset1 = input_sets[i] if i == 0 else output
        dataset2 = input_sets[i + 1]
    
        merge_datasets(dataset1, dataset2, output)