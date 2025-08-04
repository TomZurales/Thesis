import numpy as np
import matplotlib.pyplot as plt
import random

def plot_observations_for_world(world_num):
    """
    Plot observations for a specific world number.
    
    Args:
        world_num (int): The world number to plot observations for
    
    The function plots:
    - Red points for observation_status = 0
    - Green points for observation_status = 1
    - No points for observation_status = 2
    """
    # Load poses data
    poses = np.loadtxt('poses.csv', delimiter=',')
    
    # Load observations data
    observations = np.loadtxt('observations.csv', delimiter=',', dtype=int)
    
    # Filter observations for the specified world
    world_observations = observations[observations[:, 0] == world_num]
    
    if len(world_observations) == 0:
        print(f"No observations found for world {world_num}")
        return
    
    # Prepare data for plotting
    red_points = []
    green_points = []
    
    for obs in world_observations:
        _, pose_num, obs_status = obs
        
        # Skip if observation_status is 2
        if obs_status == 2:
            continue
            
        # Get the pose coordinates
        if pose_num < len(poses):
            x, y, z = poses[pose_num]
            
            if obs_status == 0:
                red_points.append([x, y, z])
            elif obs_status == 1:
                green_points.append([x, y, z])
    
    # Convert to numpy arrays
    red_points = np.array(red_points)
    green_points = np.array(green_points)
    
    # Create 3D plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot red points (observation_status = 0)
    if len(red_points) > 0:
        ax.scatter(red_points[:, 0], red_points[:, 1], red_points[:, 2], 
                  c='red', s=20, alpha=0.6, label='Status 0')
    
    # Plot green points (observation_status = 1)
    if len(green_points) > 0:
        ax.scatter(green_points[:, 0], green_points[:, 1], green_points[:, 2], 
                  c='green', s=20, alpha=0.6, label='Status 1')
    
    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'Observations for World {world_num}')
    
    # Lock all axes to range 0 to 1
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    
    # Add legend if there are points to show
    if len(red_points) > 0 or len(green_points) > 0:
        ax.legend()
    
    # Show the plot
    plt.show()
    
    # Print summary
    print(f"World {world_num} summary:")
    print(f"  Red points (status 0): {len(red_points)}")
    print(f"  Green points (status 1): {len(green_points)}")

# Example usage:
plot_observations_for_world(random.randint(0, 3294))

