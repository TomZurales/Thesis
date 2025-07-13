import numpy as np

import matplotlib.pyplot as plt

point_pose = (-1.5, 2.35)

# Create a 2D grid
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)

# Define centered 2D Gaussian function
def gaussian_2d(x, y, center_x=0, center_y=0, sigma=1.0):
    return np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * sigma**2))

# Calculate the Gaussian values
# Create randomly positioned Gaussians
Z = np.zeros_like(X)

# Random generation parameters
num_gaussians = 100
sigma = 0.45  # Gaussian spread

# Generate random positions along a path (like a car driving)
np.random.seed(42)  # For reproducible results

# Start position (outside quadrant I)
start_x, start_y = -2.0, -2.0
path_x = [start_x]
path_y = [start_y]

# Generate path parameters
num_steps = num_gaussians - 1
step_size = 0.3  # How far the car moves each step
turn_probability = 0.3  # Probability of changing direction
current_direction = np.random.uniform(0, 2*np.pi)  # Random initial direction

for i in range(num_steps):
    # Occasionally change direction (simulating turns)
    if np.random.random() < turn_probability:
        current_direction += np.random.uniform(-np.pi/2, np.pi/2)
    
    # Calculate next position
    next_x = path_x[-1] + step_size * np.cos(current_direction)
    next_y = path_y[-1] + step_size * np.sin(current_direction)
    
    # Check boundaries and avoid quadrant I
    # If we hit a boundary or enter quadrant I, turn around
    if (next_x > 3 or next_x < -3 or next_y > 3 or next_y < -3 or 
        (next_x > 0 and next_y > 0)):
        # Turn around (reverse direction with some randomness)
        current_direction += np.pi + np.random.uniform(-np.pi/4, np.pi/4)
        next_x = path_x[-1] + step_size * np.cos(current_direction)
        next_y = path_y[-1] + step_size * np.sin(current_direction)
        
        # Clamp to boundaries if still outside
        next_x = np.clip(next_x, -3, 3)
        next_y = np.clip(next_y, -3, 3)
        
        # If still in quadrant I, force to a safe location
        if next_x > 0 and next_y > 0:
            next_x = -0.5
            next_y = -0.5
    
    path_x.append(next_x)
    path_y.append(next_y)

random_x = np.array(path_x)
random_y = np.array(path_y)

# Calculate slope for the dotted line (from origin to point_pose)
slope = point_pose[1] / point_pose[0]  # y/x

for center_x, center_y in zip(random_x, random_y):
    # Determine if this should be negative based on:
    # - Right of the dotted line (y < slope * x) AND below y=0
    if center_y > slope * center_x and center_y < 0:
        sign = 1
    else:
        sign = -1
    
    # Add this Gaussian to the total
    Z += sign * gaussian_2d(X, Y, center_x=center_x, center_y=center_y, sigma=sigma)

# Normalize Z to the range [-1, 1]
Z_min = np.min(Z)
Z_max = np.max(Z)
Z = 2 * (Z - Z_min) / (Z_max - Z_min) - 1

# Create the plot
plt.figure(figsize=(8, 6))
contour = plt.contourf(X, Y, Z, levels=200, cmap='RdBu_r')
plt.colorbar(contour, label='Combined Gaussian Value')

# Draw black rectangle from (0,0) to (3,3)
from matplotlib.patches import Rectangle, Circle
rect = Rectangle((0, 0), 3, 3, facecolor='white', edgecolor='black', linewidth=1.5)
plt.gca().add_patch(rect)
point = Circle(point_pose, 0.05, color='black')
plt.gca().add_patch(point)

# Plot the car's path
plt.plot(random_x, random_y, 'g-', linewidth=1, alpha=0.6, label='Car Path')
plt.scatter(random_x[::5], random_y[::5], c='green', s=15, alpha=0.8, zorder=5)  # Show every 5th measurement point

# Plot dotted line through origin and point_pose, only for x >= point_pose[0]
# Calculate slope of line through origin and point_pose
slope = point_pose[1] / point_pose[0]  # y/x
# Create x values from point_pose[0] to the right edge of the plot
x_line = np.linspace(point_pose[0], 3, 100)
y_line = slope * x_line
# Clip the line to stay within the y-axis bounds
mask = (y_line >= -3) & (y_line <= 3)
x_line_clipped = x_line[mask]
y_line_clipped = y_line[mask]
plt.plot(x_line_clipped, y_line_clipped, 'k--', linewidth=2, alpha=0.8)

plt.xlabel('X')
plt.ylabel('Y')
plt.title('Car Path with Measurements (Avoiding Quadrant I)')
plt.xlim(-3, 3)
plt.ylim(-3, 3)
plt.axis('equal')
plt.grid(True, alpha=0.3)
plt.show()