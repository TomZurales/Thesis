import numpy as np
import matplotlib.pyplot as plt

def generate_point():
    x = 100
    y = 100
    while x > 10 or y > 10:
        if np.random.uniform(0, 1) < 0.2:
            # Outlier data
            x = np.random.uniform(0, 10)
            y = np.random.uniform(0, 10)
        else:
            # Good data
            val = np.random.uniform(0, 10)
            x = val + np.random.normal(val, .15)
            y = val + np.random.normal(val, .25)
    return x, y

# Generate 100 data points
points = [generate_point() for _ in range(100)]
x_coords = [point[0] for point in points]
y_coords = [point[1] for point in points]

def create_line_and_colors(x_coords, y_coords, seed_value):
    """Create line fit and color assignment for given seed"""
    np.random.seed(seed_value)
    selected_indices = np.random.choice(len(points), size=5, replace=False)
    selected_x = [x_coords[i] for i in selected_indices]
    selected_y = [y_coords[i] for i in selected_indices]
    
    # Fit a line through the selected points
    coefficients = np.polyfit(selected_x, selected_y, 1)
    slope, intercept = coefficients
    
    # Generate line points for plotting
    x_line = np.linspace(0, 10, 100)
    y_line = slope * x_line + intercept
    
    # Calculate distance from each point to the line
    a = -slope
    b = 1
    c = -intercept
    
    distances = []
    for x, y in zip(x_coords, y_coords):
        distance = abs(a * x + b * y + c) / np.sqrt(a**2 + b**2)
        distances.append(distance)
    
    # Determine colors based on distance to line
    colors = []
    for i, distance in enumerate(distances):
        if i in selected_indices:
            colors.append('red')  # Selected points remain red
        elif distance <= 0.5:
            colors.append('green')  # Points within 0.5 of line are green
        else:
            colors.append('blue')  # Other points remain blue
    
    return x_line, y_line, colors

# Create data for second and third plots
x_line2, y_line2, colors2 = create_line_and_colors(x_coords, y_coords, 42)

# For third plot, create best fit line using only the "good data" points
# We need to regenerate with the same seed to identify which points are "good data"
np.random.seed(42)  # Use same seed as original data generation
good_data_x = []
good_data_y = []
all_x = []
all_y = []

for _ in range(100):
    x = 100
    y = 100
    while x > 10 or y > 10:
        if np.random.uniform(0, 1) < 0.2:
            # Outlier data
            x = np.random.uniform(0, 10)
            y = np.random.uniform(0, 10)
            is_good_data = False
        else:
            # Good data
            val = np.random.uniform(0, 10)
            x = val + np.random.normal(val, .15)
            y = val + np.random.normal(val, .25)
            is_good_data = True
    
    all_x.append(x)
    all_y.append(y)
    if is_good_data:
        good_data_x.append(x)
        good_data_y.append(y)

# Fit line through good data points only
coefficients_good = np.polyfit(good_data_x, good_data_y, 1)
slope_good, intercept_good = coefficients_good
x_line3 = np.linspace(0, 10, 100)
y_line3 = slope_good * x_line3 + intercept_good

# Create colors for third plot: green for good data, blue for outliers
colors3 = []
good_idx = 0
outlier_idx = 0
np.random.seed(42)  # Reset seed to match generation order
for i in range(100):
    x_temp = 100
    y_temp = 100
    while x_temp > 10 or y_temp > 10:
        if np.random.uniform(0, 1) < 0.2:
            # Outlier data
            x_temp = np.random.uniform(0, 10)
            y_temp = np.random.uniform(0, 10)
            colors3.append('blue')
            break
        else:
            # Good data
            val = np.random.uniform(0, 10)
            x_temp = val + np.random.normal(val, .15)
            y_temp = val + np.random.normal(val, .25)
            colors3.append('green')
            break

# Create the three side-by-side plots
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

# Plot 1: All points in blue
ax1.scatter(x_coords, y_coords, s=20, alpha=0.7, c='blue')
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='both', which='major')
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)

# Plot 2: Current analysis (seed 42)
ax2.scatter(x_coords, y_coords, s=20, alpha=0.7, c=colors2)
ax2.plot(x_line2, y_line2, 'red', linewidth=2, alpha=0.8)
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='both', which='major')
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)

# Plot 3: Different random selection (seed 123)
ax3.scatter(x_coords, y_coords, s=20, alpha=0.7, c=colors3)
ax3.plot(x_line3, y_line3, 'red', linewidth=2, alpha=0.8)
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='both', which='major')
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 10)

plt.tight_layout()

# Add legend at the bottom
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Random Sample'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Points that Fit Model'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Outliers')
]
fig.legend(handles=legend_elements, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.02))

# Adjust layout to make room for legend
plt.subplots_adjust(bottom=0.15)

plt.show()
