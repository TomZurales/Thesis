import numpy as np

def cartesian_to_polar(x: float, y: float, relative_to: tuple[float, float] = (0.0, 0.0)) -> tuple[float, float]:
    r = np.hypot(x - relative_to[0], y - relative_to[1])
    theta = np.arctan2(y - relative_to[1], x - relative_to[0]) % (2 * np.pi)
    return r, theta

def polar_to_cartesian(r: float, theta: float, relative_to: tuple[float, float] = (0.0, 0.0)) -> tuple[float, float]:
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x + relative_to[0], y + relative_to[1]

def cartesian_to_spherical(
    x: float, y: float, z: float,
    relative_to: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> tuple[float, float, float]:
    """Return (r, theta, phi) where theta is azimuth in [0, 2π) and phi is
    polar angle in [0, π] (0 = +z pole, π = −z pole)."""
    dx = x - relative_to[0]
    dy = y - relative_to[1]
    dz = z - relative_to[2]
    r = float(np.sqrt(dx * dx + dy * dy + dz * dz))
    if r == 0.0:
        return 0.0, 0.0, np.pi / 2
    theta = float(np.arctan2(dy, dx) % (2 * np.pi))
    phi = float(np.arccos(np.clip(dz / r, -1.0, 1.0)))
    return r, theta, phi