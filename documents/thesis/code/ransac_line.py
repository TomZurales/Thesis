import numpy as np
import matplotlib.pyplot as plt

def generate_point():
    if np.random.uniform(0, 1) < 0.2:
        # Generate a point with a specific distribution
        x = np.random.uniform(0, 10)
        y = np.random.uniform(0, 10)
    else:
        # linear data
        val = np.random.uniform(0, 10)
        x = val + np.random.(0, 10)
        y = x
    return x, y

# Generate 100 data points
points = [generate_point() for _ in range(100)]
x_coords = [point[0] for point in points]
y_coords = [point[1] for point in points]

# Create the scatter plot
plt.figure(figsize=(8, 8))
plt.scatter(x_coords, y_coords, s=20, alpha=0.7)
plt.grid(True, alpha=0.3)
plt.tick_params(axis='both', which='major')
plt.xlim(0, None)  # Ensure positive x
plt.ylim(0, None)  # Ensure positive y
plt.show()
