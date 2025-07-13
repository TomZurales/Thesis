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
# Create a 10x10 grid of Gaussians centered around the origin
Z = np.zeros_like(X)

# Grid parameters
grid_size = 10
spacing = 6 / (grid_size - 1)  # Spacing to fit in the -3 to 3 range
sigma = 0.25  # Larger sigma for more spread

# Create grid centers
grid_centers_x = np.linspace(-3, 3, grid_size)
grid_centers_y = np.linspace(-3, 3, grid_size)

for i, center_x in enumerate(grid_centers_x):
    for j, center_y in enumerate(grid_centers_y):
        # Determine if this should be negative based on quadrant
        # Negative in quadrant II (x < 0, y > 0) and quadrant IV (x > 0, y < 0)
        if (center_x < 0 and center_y > 0):
            sign = 1
        else:
            sign = -1
        
        # Add this Gaussian to the total
        Z += sign * gaussian_2d(X, Y, center_x=center_x, center_y=center_y, sigma=sigma)

# Create the plot
plt.figure(figsize=(8, 6))
contour = plt.contourf(X, Y, Z, levels=200, cmap='RdBu_r')
plt.colorbar(contour, label='Combined Gaussian Value')

# Draw black rectangle from (0,0) to (3,3)
from matplotlib.patches import Rectangle, Circle
rect = Rectangle((0, 0), 3, 3, facecolor='grey')
plt.gca().add_patch(rect)
point = Circle(point_pose, 0.05, color='black')
plt.gca().add_patch(point)

# Plot dotted line through origin and point_pose, only for x >= point_pose[0]
# Calculate slope of line through origin and point_pose
slope = point_pose[1] / point_pose[0]  # y/x
# Create x values from point_pose[0] to the right edge of the plot
x_line = np.linspace(point_pose[0], 3, 100)
y_line = slope * x_line
plt.plot(x_line, y_line, 'k--', linewidth=2, alpha=0.8)

plt.xlabel('X')
plt.ylabel('Y')
plt.title('10x10 Grid of Gaussians (Negative in Quadrants II & IV)')
plt.axis('equal')
plt.grid(True, alpha=0.3)
plt.show()