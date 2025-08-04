from constants import MIN_OBS_DIST, MAX_OBS_DIST
import random
import math

class Viewpoint:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

        length = (x**2 + y**2 + z**2) ** 0.5
        if length < MIN_OBS_DIST or length > MAX_OBS_DIST:
            raise ValueError(f"Viewpoint coordinates must be between {MIN_OBS_DIST} and {MAX_OBS_DIST} in magnitude, got {length}")
        
    @staticmethod
    def random():
        while True:
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            z = random.uniform(-1, 1)
            length = (x**2 + y**2 + z**2) ** 0.5
            if length >= MIN_OBS_DIST and length <= MAX_OBS_DIST:
                break
        return Viewpoint(x, y, z)
    
    def __repr__(self):
        return f"Viewpoint(x={self.x}, y={self.y}, z={self.z})"
    
    def angular_distance(self, other) -> float:
        # Calculate dot product
        dot_product = self.x * other.x + self.y * other.y + self.z * other.z

        # Calculate magnitudes
        magnitude_self = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        magnitude_other = math.sqrt(other.x**2 + other.y**2 + other.z**2)

        # Avoid division by zero
        if magnitude_self == 0 or magnitude_other == 0:
            return 0

        # Calculate cosine of angle and clamp to [-1, 1] to handle floating point errors
        cos_angle = max(-1, min(1, dot_product / (magnitude_self * magnitude_other)))

        # Return angle in radians
        return math.acos(cos_angle)
        
    def euclidean_distance(self, other):
        # Calculate the squared differences for each dimension
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        
        # Return the Euclidean distance (square root of sum of squared differences)
        return math.sqrt(dx**2 + dy**2 + dz**2)
    
if __name__ == "__main__":
    # Example usage
    vp = Viewpoint.random()
    print(vp)
    
    try:
        invalid_vp = Viewpoint(2, 2, 2)  # This should raise an error
    except ValueError as e:
        print(e)
    
    valid_vp = Viewpoint(0.5, 0.5, 0.5)
    print(valid_vp)