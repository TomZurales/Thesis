import math

from observability_models.observability_model import ObservabilityModel

class DiscreteBoundary(ObservabilityModel):
    def __init__(self, n: int):
        self.n = n
        self.max_seen = [0] * n
        self.min_unseen = [float('inf')] * n
        self.ambiguous_positives = [0] * n
        self.ambiguous_negatives = [0] * n

    def query(self, position: tuple[int, int]) -> float:
        bin = self._select_bin(position)
        r = (position[0]**2 + position[1]**2)**0.5
        if r <= self.max_seen[bin]:
            if r < self.min_unseen[bin]:
                return 1.0
            else:
                if self.ambiguous_positives[bin] == 0:
                    self.ambiguous_positives[bin] = self.ambiguous_negatives[bin]
                return self.ambiguous_positives[bin] / (self.ambiguous_positives[bin] + self.ambiguous_negatives[bin] + 1e-6)
        else:
            return 0.0
        
    def integrate(self, observations: list[tuple[float, float, bool]]):
        for x, y, seen in observations:
            bin = self._select_bin((x, y))
            r = (x**2 + y**2)**0.5
            if seen and r > self.max_seen[bin]:
                self.max_seen[bin] = r
            elif not seen and r < self.min_unseen[bin]:
                self.min_unseen[bin] = r
        for x, y, seen in observations:
            bin = self._select_bin((x, y))
            r = (x**2 + y**2)**0.5
            if seen and r > self.min_unseen[bin]:
                self.ambiguous_positives[bin] += 1
            elif not seen and r < self.max_seen[bin] and r > self.min_unseen[bin]:
                self.ambiguous_negatives[bin] += 1

        

    def _select_bin(self, position: tuple[int, int]) -> int:
        angle = math.atan2(position[1], position[0])
        if angle < 0:
            angle += 2 * math.pi
        return int(angle / (2 * math.pi) * self.n) % self.n
