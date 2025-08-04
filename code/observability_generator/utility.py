import math

class ObservationOld:
    x: float
    y: float
    z: float
    seen: float

    age = 0

    def __init__(self, x, y, z, seen):
        self.x = x
        self.y = y
        self.z = z
        self.seen = seen

    def angular_distance(self, other):
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