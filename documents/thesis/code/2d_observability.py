import numpy as np

import matplotlib.pyplot as plt

# Create figure and polar subplot
fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))

# Plot point at center
ax.plot(0, 0, 'ro', markersize=8, label='p')
ax.text(0, 0.1, 'p', ha='center', va='bottom', fontsize=12)

# Draw straight black line from 7π/4 to π/4 at distance 0.4
theta_line = [7 * np.pi / 4, np.pi / 4]
r_line = [0.4, 0.4]

# Create filled regions - blue from center to wall, red from wall to edge
theta_full = np.linspace(0, 2*np.pi, 360)

# For each angle, determine if there's a wall
wall_distance = np.full_like(theta_full, 1.0)  # Default to edge of plot
# Set wall distance to 0.4 for angles between 7π/4 and π/4 (crossing through 0)
for i, theta in enumerate(theta_full):
    # Check if angle is in the range 7π/4 to π/4 (crossing 0)
    if theta >= 7*np.pi/4 or theta <= np.pi/4:
        wall_distance[i] = 0.4

# Create blue region (center to wall)
r_blue_inner = np.zeros_like(theta_full)
r_blue_outer = wall_distance
ax.fill_between(theta_full, r_blue_inner, r_blue_outer, alpha=0.3, color='blue')

# Create red region (wall to edge)
r_red_inner = wall_distance
r_red_outer = np.ones_like(theta_full)
ax.fill_between(theta_full, r_red_inner, r_red_outer, alpha=0.3, color='red')

# Draw the wall line on top
ax.plot(theta_line, r_line, 'k-', linewidth=2)

# Set up the plot
ax.set_ylim(0, 1)
ax.set_yticklabels([])  # Remove radial distance labels
# Create radian labels as fractions of pi
radian_labels = ['0', 'π/4', 'π/2', '3π/4', 'π', '5π/4', '3π/2', '7π/4']
ax.set_thetagrids(np.degrees(np.linspace(0, 2*np.pi, 8, endpoint=False)), 
                  labels=radian_labels)
ax.set_title('Radial Plot')
ax.grid(True)

plt.show()