import numpy as np

import matplotlib.pyplot as plt

# Create a 2D grid
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)

# Define centered 2D Gaussian function
def gaussian_2d(x, y, center_x=0, center_y=0, sigma=1.0):
    return np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * sigma**2))

# Calculate the Gaussian values
Z_positive = gaussian_2d(X, Y, center_x=0, center_y=0, sigma=1.0)  # Centered positive Gaussian
Z_negative = -gaussian_2d(X, Y, center_x=1.5, center_y=-1.5, sigma=0.8)  # Bottom right negative Gaussian

# Combine the two Gaussians
Z = Z_positive + Z_negative

# Create the plot
plt.figure(figsize=(8, 6))
contour = plt.contourf(X, Y, Z, levels=200, cmap='RdBu_r')
plt.colorbar(contour, label='Combined Gaussian Value')

plt.xlabel('X')
plt.ylabel('Y')
plt.title('2D Centered Gaussian Function')
plt.axis('equal')
plt.grid(True, alpha=0.3)
plt.show()