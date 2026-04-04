import os
import numpy as np
import heapq
import shutil

class TimedPose:
    timestamp: float
    x: float
    y: float
    z: float
    rx: float
    ry: float
    rz: float
    rw: float

    def __init__(self, timestamp: float, x: float, y: float, z: float, rx: float, ry: float, rz: float, rw: float):
        self.timestamp = timestamp
        self.x = x
        self.y = y
        self.z = z
        self.rx = rx
        self.ry = ry
        self.rz = rz
        self.rw = rw

    @classmethod
    def from_string(cls, data_str: str):
        data = data_str.split(" ")
        return TimedPose(
            float(data[0]),
            float(data[1]),
            float(data[2]),
            float(data[3]),
            float(data[4]),
            float(data[5]),
            float(data[6]),
            float(data[7]),
        )

    def __repr__(self):
        return f"{self.timestamp} {self.x} {self.y} {self.z} {self.rx} {self.ry} {self.rz} {self.rw}"

    def __lt__(self, other):
        return self.timestamp < other.timestamp
        
def average_poses(poses: list[TimedPose]) -> TimedPose:
    """
    Average a list of TimedPose instances.
    Does simple average for timestamp, x, y, z and quaternion average for rotation.
    """
    
    if not poses:
        return None
    
    # Simple averages
    avg_timestamp = np.mean([p.timestamp for p in poses])
    avg_x = np.mean([p.x for p in poses])
    avg_y = np.mean([p.y for p in poses])
    avg_z = np.mean([p.z for p in poses])
    
    # Quaternion average using eigenvalue decomposition
    quaternions = [(p.rx, p.ry, p.rz, p.rw) for p in poses]
    Q = np.array(quaternions)
    
    # Compute the matrix M = sum of q * q^T
    M = np.zeros((4, 4))
    for q in Q:
        q_arr = np.array([q[3], q[0], q[1], q[2]])  # (w, x, y, z)
        M += np.outer(q_arr, q_arr)
    
    M /= len(quaternions)
    
    # The eigenvector corresponding to the largest eigenvalue is the average
    _, eigenvectors = np.linalg.eigh(M)
    avg_q = eigenvectors[:, -1]  # Largest eigenvalue's eigenvector
    
    # Return in (rx, ry, rz, rw) format
    avg_rx, avg_ry, avg_rz, avg_rw = avg_q[1], avg_q[2], avg_q[3], avg_q[0]
    
    return TimedPose(avg_timestamp, avg_x, avg_y, avg_z, avg_rx, avg_ry, avg_rz, avg_rw)

# results_dir = 'results'
# trajectories = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]

# run_types = ["Baseline", "VBEE"]
# result_types = ["Frame", "KeyFrame"]

# # print(trajectories)
# for trajectory in trajectories:
#     trajectory_dir = os.path.join(results_dir, trajectory)
#     iterations = [d for d in os.listdir(trajectory_dir) if os.path.isdir(os.path.join(trajectory_dir, d)) and d != "average"]

#     if os.path.exists(os.path.join(trajectory_dir, "average")):
#         shutil.rmtree(os.path.join(trajectory_dir, "average"))
#     os.mkdir(os.path.join(trajectory_dir, "average"))
#     average_dir = os.path.join(trajectory_dir, "average")

#     for run_type in run_types:
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


