import numpy as np

import matplotlib.pyplot as plt

# Create figure and polar subplot
fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))

# Plot point at center
ax.plot(0, 0, 'ro', markersize=8, label='p')
ax.text(0, 0.1, 'p', ha='center', va='bottom', fontsize=12)

# Draw black line from 7π/4 to π/4 at distance 0.4
theta_start = 7 * np.pi / 4
theta_end = np.pi / 4
# Create arc from 7π/4 to π/4 (going clockwise through 0)
theta_arc = np.linspace(theta_start, theta_end + 2*np.pi, 100)
r_arc = np.full_like(theta_arc, 0.4)
ax.plot(theta_arc, r_arc, 'k-', linewidth=2)

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