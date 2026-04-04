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

# Create data for second and third plots with reselection logic
def get_valid_line_and_colors(x_coords, y_coords, initial_seed, min_green=None, max_green=None):
    """Get line and colors, reselecting if green point count doesn't meet criteria"""
    seed = initial_seed
    attempts = 0
    max_attempts = 1000
    
    while attempts < max_attempts:
        x_line, y_line, colors = create_line_and_colors(x_coords, y_coords, seed)
        green_count = colors.count('green')
        
        # Check if criteria are met
        valid = True
        if min_green is not None and green_count < min_green:
            valid = False
        if max_green is not None and green_count > max_green:
            valid = False
        
        if valid:
            return x_line, y_line, colors, green_count
        
        seed += 1
        attempts += 1
    
    # If no valid solution found, return the last attempt
    return x_line, y_line, colors, green_count

# Create best fit line for all data (first plot)
all_coefficients = np.polyfit(x_coords, y_coords, 1)
all_slope, all_intercept = all_coefficients
all_x_line = np.linspace(0, 10, 100)
all_y_line = all_slope * all_x_line + all_intercept

# Calculate colors for all data points based on best fit line
all_a = -all_slope
all_b = 1
all_c = -all_intercept

all_colors = []
for x, y in zip(x_coords, y_coords):
    distance = abs(all_a * x + all_b * y + all_c) / np.sqrt(all_a**2 + all_b**2)
    if distance <= 0.5:
        all_colors.append('green')  # Points within 0.5 of line are green
    else:
        all_colors.append('blue')   # Other points are blue

# Middle plot: reselect if more than 30 green points
x_line2, y_line2, colors2, green_count2 = get_valid_line_and_colors(x_coords, y_coords, 42, max_green=25)

# Right plot: reselect if less than 60 green points
x_line3, y_line3, colors3, green_count3 = get_valid_line_and_colors(x_coords, y_coords, 123, min_green=70)

print(f"Middle plot: {green_count2} green points (≤30 required)")
print(f"Right plot: {green_count3} green points (≥60 required)")

# Create the three side-by-side plots
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

# Plot 1: All points with best fit line
ax1.scatter(x_coords, y_coords, s=20, alpha=0.7, c=all_colors)
ax1.plot(all_x_line, all_y_line, 'red', linewidth=2, alpha=0.8)
ax1.grid(True, alpha=0.3)
ax1.tick_params(axis='both', which='major', labelsize=12)
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.set_title('Raw Data with Best Fit', fontsize=18)

# Plot 2: Current analysis (seed 42)
ax2.scatter(x_coords, y_coords, s=20, alpha=0.7, c=colors2)
ax2.plot(x_line2, y_line2, 'red', linewidth=2, alpha=0.8)
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='both', which='major', labelsize=12)
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.set_title('Random Sample with Low Consensus', fontsize=18)

# Plot 3: Different random selection (seed 123)
ax3.scatter(x_coords, y_coords, s=20, alpha=0.7, c=colors3)
ax3.plot(x_line3, y_line3, 'red', linewidth=2, alpha=0.8)
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='both', which='major', labelsize=12)
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 10)
ax3.set_title('Random Sample with High Consensus', fontsize=18)

plt.tight_layout()

# Add legend at the bottom
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Random Sample'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Points that Fit Model'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Points that Do Not Fit Model'),
]
fig.legend(handles=legend_elements, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.0), fontsize=18)

# Adjust layout to make room for legend
plt.subplots_adjust(bottom=0.15)

plt.show()
