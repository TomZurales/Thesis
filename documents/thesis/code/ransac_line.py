import numpy as np
import matplotlib.pyplot as plt

def generate_point():
    if rand
    """
    Function to generate a single X,Y coordinate.
    Implement your own logic here.
    Should return a tuple (x, y) where both x and y are positive.
    """
    # Placeholder implementation - replace with your own
    x = np.random.uniform(0, 10)
    y = np.random.uniform(0, 10)
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
