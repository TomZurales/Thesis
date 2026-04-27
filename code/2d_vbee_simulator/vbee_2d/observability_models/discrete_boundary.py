import math

def clamp(value, minmax_value):
    return max(-minmax_value, min(minmax_value, value))

def map_value(value, from_min, from_max, to_min, to_max):
    if from_max == from_min:
        return to_min
    return to_min + (to_max - to_min) * ((value - from_min) / (from_max - from_min))

class DiscreteBoundary:
    def __init__(self, n: int, k: int = 5, ambiguous_range = 0.5):
        self.n = n
        self.k = k
        self.ambiguous_range = ambiguous_range
        self.max_seen = [0] * n
        self.bin_observabilities = [0] * n
        self.bin_ambiguous = [k] * n
        self.min_unseen = [float('inf')] * n

    def query(self, position: tuple[int, int]) -> float:
        x, y = position
        r = (x**2 + y**2)**0.5
        bin = self._select_bin(position)
        if r <= self.max_seen[bin]:
            if r < self.min_unseen[bin]:
                return 1.0
            else:
                return map_value(self.bin_ambiguous[bin], 0, 2 * self.k, 0.5 - (self.ambiguous_range / 2), 0.5 + (self.ambiguous_range / 2))
        else:
            return 0.0
    
    def update(self, observation: tuple[float, float, bool]) -> float:
        x, y, obs = observation
        r = (x**2 + y**2)**0.5
        bin = self._select_bin((x, y))

        updated = False

        if obs:
            if r > self.max_seen[bin]:
                self.max_seen[bin] = r
                updated = True
        else:
            if r < self.min_unseen[bin]:
                self.min_unseen[bin] = r
                updated = True

        if r <= self.max_seen[bin] and r >= self.min_unseen[bin]:
            if obs:
                self.bin_ambiguous[bin] = min(2 * self.k, self.bin_ambiguous[bin] + 1)
            else:
                self.bin_ambiguous[bin] = max(0, self.bin_ambiguous[bin] - 1)
            updated = True

        if updated: # Update the observability(integrate) if there was a change in the max_seen or min_unseen
            # There will be two sections: [0 to min_unseen), [min_unseen to max_seen]
            # The volume of each section is calculated, and multiplied by the query value of that section to get the observability contribution of that section
            # The total observability is the sum of the contributions of all sections

            if self.min_unseen[bin] < self.max_seen[bin]:
                # Two sections
                s1_vol = math.pi * (self.min_unseen[bin] ** 2) / self.n
                s2_vol = (math.pi * (self.max_seen[bin] ** 2) / self.n) - s1_vol
                self.bin_observabilities[bin] = s1_vol + (map_value(self.bin_ambiguous[bin], 0, 2 * self.k, 0.5 - (self.ambiguous_range / 2), 0.5 + (self.ambiguous_range / 2)) * s2_vol)
            else:
                # One section
                self.bin_observabilities[bin] = math.pi * (self.max_seen[bin] ** 2) / self.n

        return sum(self.bin_observabilities)

    def getObservability(self) -> float:
        return sum(self.bin_observabilities)
    
    def _select_bin(self, position: tuple[int, int]) -> int:
        angle = math.atan2(position[1], position[0])
        if angle < 0:
            angle += 2 * math.pi
        return int(angle / (2 * math.pi) * self.n) % self.n