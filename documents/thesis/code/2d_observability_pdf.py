import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import vonmises

# Parameters
kappa = 4  # concentration parameter
mu = 0     # mean direction (radians)

# Generate theta values
theta = np.linspace(0, 2*np.pi, 1000)
r = vonmises.pdf(theta, kappa, loc=mu)  # PDF values

# Plot
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(111, polar=True)

ax.plot(theta, r, label=f'von Mises ($\\kappa={kappa}$)', lw=2)
ax.fill_between(theta, 0, r, alpha=0.3)

# Optional aesthetic tweaks
ax.set_rticks([])  # remove radial ticks
ax.set_theta_zero_location("N")  # zero at top
ax.set_theta_direction(-1)       # clockwise
ax.legend(loc='lower left')

plt.title("Wrapped von Mises PDF")
plt.show()
