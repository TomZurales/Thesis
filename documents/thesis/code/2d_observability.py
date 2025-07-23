import numpy as np

import matplotlib.pyplot as plt

# Create figure and polar subplot
fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))

# Plot point at center
ax.plot(0, 0, 'ro', markersize=8, label='p')
ax.text(0, 0.1, '$p$', ha='center', va='bottom', fontsize=12)

# Color the area from 7π/4 to π/4 where r < 0.4 blue
theta_range = np.linspace(7*np.pi/4, np.pi/4 + 2*np.pi, 100)  # Add 2π to handle wrap-around
r_inner = np.zeros_like(theta_range)
r_outer = np.full_like(theta_range, 0.4)
ax.fill_between(theta_range, r_inner, r_outer, alpha=0.3, color='blue')

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