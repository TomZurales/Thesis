import numpy as np
import matplotlib.pyplot as plt

def generate_point():
    x = 100
    y = 100
    while x > 10 or y > 10:
        if np.random.uniform(0, 1) < 0.2:
            # Generate a point with a specific distribution
            x = np.random.uniform(0, 10)
            y = np.random.uniform(0, 10)
        else:
            # linear data
            val = np.random.uniform(0, 10)
            x = val + np.random.normal(val, .15)
            y = val + np.random.normal(val, .25)
    return x, y

# Generate 100 data points
points = [generate_point() for _ in range(100)]
x_coords = [point[0] for point in points]
y_coords = [point[1] for point in points]

# Randomly select 5 points for line fitting
np.random.seed(42)  # For reproducible results
selected_indices = np.random.choice(len(points), size=5, replace=False)
selected_x = [x_coords[i] for i in selected_indices]
selected_y = [y_coords[i] for i in selected_indices]

# Fit a line through the selected points
coefficients = np.polyfit(selected_x, selected_y, 1)
slope, intercept = coefficients

# Generate line points for plotting
x_line = np.linspace(0, max(x_coords), 100)
y_line = slope * x_line + intercept

# Create the scatter plot
plt.figure(figsize=(8, 8))
plt.scatter(x_coords, y_coords, s=20, alpha=0.7)
plt.grid(True, alpha=0.3)
plt.tick_params(axis='both', which='major')
plt.xlim(0, None)  # Ensure positive x
plt.ylim(0, None)  # Ensure positive y
plt.show()
