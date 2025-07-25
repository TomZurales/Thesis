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

# Generate random positions with better distribution
np.random.seed(42)  # For reproducible results

# Use Poisson disk sampling for more even distribution
def generate_poisson_disk_samples(width, height, min_distance, max_attempts=30):
    """Generate points with minimum distance constraint for more even distribution"""
    points = []
    
    # Start with a random first point
    first_point = np.array([np.random.uniform(-width/2, width/2), 
                           np.random.uniform(-height/2, height/2)])
    points.append(first_point)
    
    # Generate more points
    while len(points) < num_gaussians:
        # Try to place a new point
        for _ in range(max_attempts):
            new_point = np.array([np.random.uniform(-width/2, width/2), 
                                 np.random.uniform(-height/2, height/2)])
            
            # Check if it's far enough from existing points
            if all(np.linalg.norm(new_point - existing) >= min_distance 
                   for existing in points):
                points.append(new_point)
                break
        else:
            # If we can't place a point, reduce the minimum distance
            min_distance *= 0.9
    
    return np.array(points)

# Generate well-distributed points
min_distance = 0.4  # Minimum distance between points
points = generate_poisson_disk_samples(6, 6, min_distance)
random_x = points[:, 0]
random_y = points[:, 1]

# Reroll any Gaussians that fall in quadrant I (x > 0 and y > 0)
quadrant_I_mask = (random_x > 0) & (random_y > 0)

while np.any(quadrant_I_mask):
    # For points in quadrant I, generate new positions outside quadrant I
    num_rerolls = np.sum(quadrant_I_mask)
    
    for i in range(num_rerolls):
        # Find a valid position outside quadrant I
        valid_position = False
        attempts = 0
        while not valid_position and attempts < 100:
            new_x = np.random.uniform(-3, 3)
            new_y = np.random.uniform(-3, 3)
            
            # Check if it's outside quadrant I and far enough from other points
            if not (new_x > 0 and new_y > 0):
                new_point = np.array([new_x, new_y])
                existing_points = np.column_stack([random_x, random_y])
                
                if all(np.linalg.norm(new_point - existing) >= min_distance * 0.5
                       for j, existing in enumerate(existing_points) 
                       if not quadrant_I_mask[j]):
                    # Find the first point in quadrant I and replace it
                    idx = np.where(quadrant_I_mask)[0][i]
                    random_x[idx] = new_x
                    random_y[idx] = new_y
                    valid_position = True
            
            attempts += 1
    
    # Update the mask
    quadrant_I_mask = (random_x > 0) & (random_y > 0)

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

# Add small dots at each Gaussian center
plt.scatter(random_x, random_y, c='black', s=8, alpha=0.7, zorder=5)

# Draw black rectangle from (0,0) to (3,3)
from matplotlib.patches import Rectangle, Circle
rect = Rectangle((0, 0), 3, 3, facecolor='white')
# Manually draw only the left and bottom edges (not on plot border)
plt.plot([0, 0], [0, 3], 'k-', linewidth=1)  # Left edge
plt.plot([0, 3], [0, 0], 'k-', linewidth=1)  # Bottom edge
plt.gca().add_patch(rect)
point = Circle(point_pose, 0.05, color='black')
plt.gca().add_patch(point)

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
plt.title('Random Gaussians (Negative: Right of Line & Below y=0)')
plt.xlim(-3, 3)
plt.ylim(-3, 3)
plt.axis('equal')
plt.grid(True, alpha=0.3)
plt.show()