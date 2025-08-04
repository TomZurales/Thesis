from itertools import product
import random
from constants import WORLDS_FILE_PATH, WorldWallTypes, VIEWPOINTS_FILE_PATH
import os

def canonical_form(t):
    rotations = [t[i:] + t[:i] for i in range(len(t))]
    return min(rotations)

def remove_rotational_duplicates(tuples):
    seen = set()
    result = []
    for t in tuples:
        canonical = canonical_form(t)
        if canonical not in seen:
            seen.add(canonical)
            result.append(t)
    return result

def gen_all_worlds(output_path = WORLDS_FILE_PATH):
    if os.path.exists(output_path):
        print(f"Worlds file {output_path} already exists. Skipping generation.")
        return
    perms = product(range(6), repeat=6)
    good_perms = []
    for perm in perms:
        if perm[0] in (WorldWallTypes.T_NEAR, WorldWallTypes.X_NEAR, WorldWallTypes.T_NEAR_X_FAR) and perm[3] in (WorldWallTypes.T_NEAR, WorldWallTypes.X_NEAR, WorldWallTypes.T_NEAR_X_FAR):
            continue
        if perm[1] in (WorldWallTypes.T_NEAR, WorldWallTypes.X_NEAR, WorldWallTypes.T_NEAR_X_FAR) and perm[4] in (WorldWallTypes.T_NEAR, WorldWallTypes.X_NEAR, WorldWallTypes.T_NEAR_X_FAR):
            continue
        if perm[2] in (WorldWallTypes.T_NEAR, WorldWallTypes.X_NEAR, WorldWallTypes.T_NEAR_X_FAR) and perm[5] in (WorldWallTypes.T_NEAR, WorldWallTypes.X_NEAR, WorldWallTypes.T_NEAR_X_FAR):
            continue
        good_perms.append(perm)
    final_perms = remove_rotational_duplicates(good_perms)

    with open(output_path, 'w') as f:
        for perm in final_perms:
            f.write(','.join(map(str, perm)) + '\n')

def gen_random_viewpoints(n, output_path = VIEWPOINTS_FILE_PATH):
    if os.path.exists(output_path):
        # Count the number of lines, if it's not n, regenerate
        with open(output_path, 'r') as f:
            lines = f.readlines()
            if len(lines) == n:
                print(f"Poses file {output_path} already exists with {len(lines)} poses. Skipping generation.")
                return
            print(f"Poses file {output_path} exists but has {len(lines)} poses, regenerating.")
    poses = []

    for _ in range(n):
        reroll = True
        while reroll:
            pose = [random.uniform(-1, 1) for _ in range(3)]
            # Calculate the length of the pose vector
            length = sum(x ** 2 for x in pose) ** 0.5
            if(length < 0.1 or length > 1.0):
                continue
            reroll = False
            poses.append(pose)

    with open(output_path, 'w') as f:
        for pose in poses:
            f.write(','.join(map(str, pose)) + '\n')

if __name__ == "__main__":
    n_poses = 1000
    poses = gen_random_viewpoints(n_poses)

    # Write the poses to a csv
    with open('poses.csv', 'w') as f:
        for pose in poses:
            f.write(','.join(map(str, pose)) + '\n')
    print(f"Generated {n_poses} poses and saved to poses.csv")

    worlds = gen_all_worlds()
    with open('worlds.csv', 'w') as f:
        for world in worlds:
            f.write(','.join(map(str, world)) + '\n')

    for i, world in enumerate(worlds):
        with open(f"observations/{i}.csv", 'w') as f:
            for j, pose in enumerate(poses):
                result = test_world(world, *pose)
                f.write(f"{j},{result}\n")
