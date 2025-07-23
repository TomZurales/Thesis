import numpy as np

import matplotlib.pyplot as plt

# Create figure and polar subplot
fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))

# Plot point at center
ax.plot(0, 0, 'ro', markersize=8, label='p')
ax.text(0, 0.1, 'p', ha='center', va='bottom', fontsize=12)
-
# Draw straight black line from 7π/4 to π/4 at distance 0.4
theta_line = [7 * np.pi / 4, np.pi / 4]
r_line = [0.4, 0.4]

# Create filled regions - blue from center to wall, red from wall to edge
theta_full = np.linspace(0, 2*np.pi, 360)

# For each angle, determine if there's a wall
wall_distance = np.full_like(theta_full, 1.0)  # Default to edge of plot

# The wall blocks everything from 7π/4 to π/4, wrapping around through 0
# We need to handle the wrap-around properly
for i, theta in enumerate(theta_full):
    # Check if angle is in the range 7π/4 to π/4 (crossing 0)
    # This covers the angular range where the wall creates a shadow
    if theta >= 7*np.pi/4 or theta <= np.pi/4:
        # For angles where the wall exists, everything beyond 0.4 is blocked
        wall_distance[i] = 0.4
    else:
        # For angles where there's no physical wall, we need to check
        # if the line of sight intersects the wall segment
        # The wall is a chord from (7π/4, 0.4) to (π/4, 0.4)
        # Any ray from center in the "shadow" region should be blocked at distance 0.4
        
        # Convert wall endpoints to Cartesian for easier calculation
        x1 = 0.4 * np.cos(7*np.pi/4)  # Wall start point
        y1 = 0.4 * np.sin(7*np.pi/4)
        x2 = 0.4 * np.cos(np.pi/4)    # Wall end point  
        y2 = 0.4 * np.sin(np.pi/4)
        
        # Ray direction for current angle
        ray_x = np.cos(theta)
        ray_y = np.sin(theta)
        
        # Check if ray intersects the wall chord
        # Using parametric line intersection
        denom = (x2-x1)*ray_y - (y2-y1)*ray_x
        if abs(denom) > 1e-10:  # Lines are not parallel
            t = ((x2-x1)*(-y1) - (y2-y1)*(-x1)) / denom
            s = (ray_x*(-y1) - ray_y*(-x1)) / denom
            
            # Check if intersection is on both the ray (t>0) and wall segment (0<=s<=1)
            if t > 0 and 0 <= s <= 1:
                wall_distance[i] = t  # Distance to wall intersection

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