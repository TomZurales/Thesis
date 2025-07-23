import numpy as np

import matplotlib.pyplot as plt

# Create figure and polar subplot
fig, ax = plt.subplots(subplot_kw=dict(projection='polar'))

# Plot point at center
ax.plot(0, 0, 'ro', markersize=8, label='p')
ax.text(0, 0.1, 'p', ha='center', va='bottom', fontsize=12)

# Set up the plot
ax.set_ylim(0, 1)
ax.set_title('Radial Plot')
ax.grid(True)

plt.show()