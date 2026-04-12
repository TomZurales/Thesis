import numpy as np

def cartesian_to_polar(x: float, y: float, relative_to: tuple[float, float] = (0.0, 0.0)) -> tuple[float, float]:
    r = np.hypot(x - relative_to[0], y - relative_to[1])
    theta = np.arctan2(y - relative_to[1], x - relative_to[0]) % (2 * np.pi)
    return r, theta

def polar_to_cartesian(r: float, theta: float, relative_to: tuple[float, float] = (0.0, 0.0)) -> tuple[float, float]:
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x + relative_to[0], y + relative_to[1]