import numpy as np

import matplotlib.pyplot as plt

# Create a 2D grid
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)

# Define centered 2D Gaussian function
def gaussian_2d(x, y, sigma=1.0):
    return np.exp(-(x**2 + y**2) / (2 * sigma**2))

# Calculate the Gaussian values
Z = gaussian_2d(X, Y)

# Create the plot
plt.figure(figsize=(8, 6))
contour = plt.contourf(X, Y, Z, levels=200, cmap='Blues')
plt.colorbar(contour, label='Gaussian Value')

plt.xlabel('X')
plt.ylabel('Y')
plt.title('2D Centered Gaussian Function')
plt.axis('equal')
plt.grid(True, alpha=0.3)
plt.show()