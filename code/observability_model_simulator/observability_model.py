import random
import numpy as np
from scipy.spatial import ConvexHull, Delaunay, cKDTree
from utility import cartesian_to_polar, cartesian_to_spherical
from dataclasses import dataclass
from vbee import VBEE

@dataclass
class Bin:
    center: float
    positive: float = -1.0
    negative: float = float('inf')

class ObservabilityModel:
    def __init__(self):
        self.new_observations: list[tuple[tuple[int, int], bool]] = []
        self.observations: list[tuple[tuple[int, int], bool]] = []
        self.epsilon = 1e-6
        self.p_e = 0.9
    
    def add_observation(self, position: tuple[int, int], seen: bool):
        self.new_observations.append((position, seen))

    def commit(self):
        pass

    def get_p_e(self) -> float:
        return self.p_e
    
    def _update(self, position: tuple[int, int], seen: bool):
        pass

    def query(self, position: tuple[int, int]) -> float:
        pass

    def set_target(self, position: tuple[int, int]):
        self.goal = position

    def __str__(self):
        pass
    
class DiscreteBoundary(ObservabilityModel):
    def __init__(self, n: int):
        super().__init__()
        self.n = n
        self.boundaries = [0] * n
        self.bin_centers = np.array([2 * np.pi * i / n for i in range(n)])

    def _get_bin_index(self, theta: float) -> int:
        d = np.abs(theta - self.bin_centers) % (2 * np.pi)
        d = np.minimum(d, 2 * np.pi - d)
        return int(np.argmin(d))

    def _update(self, position: tuple[int, int], seen: bool):
        r, theta = cartesian_to_polar(position[0], position[1], relative_to=self.goal)
        i = self._get_bin_index(theta)
        if seen and r > self.boundaries[i]:
            self.boundaries[i] = r

    def query(self, position: tuple[int, int]) -> float:
        r, theta = cartesian_to_polar(position[0], position[1], relative_to=self.goal)
        bin = self._get_bin_index(theta)
        if r <= self.boundaries[bin]:
            return 1.0
        else:
            return 0.0

    def commit(self):
        if not self.new_observations:
            return

        # Query model before any updates for batch consistency
        queried = [
            (pos, seen, self.query(pos))
            for pos, seen in self.new_observations
        ]

        # Unique bins sampled with non-observations this session
        negative_bin_indices = set(
            self._get_bin_index(
                cartesian_to_polar(pos[0], pos[1], relative_to=self.goal)[1]
            )
            for pos, seen, _ in queried if not seen
        )

        # Equal weight per confirmed bin — one angular region, one vote
        total_weight = sum(1.0 for i in range(self.n) if self.boundaries[i] != -1)
        sampled_weight = sum(1.0 for i in negative_bin_indices if self.boundaries[i] != -1)
        coverage = sampled_weight / total_weight if total_weight > 0 else 0.0

        # Update P(E)
        for pos, seen, p_s in queried:
            if seen:
                self.p_e = np.clip(
                    self.p_e / (self.p_e + self.epsilon * (1 - self.p_e)),
                    0.1, 0.9
                )
            else:
                confidence = 2 * abs(p_s - 0.5)
                factor = 1 - coverage * confidence * p_s
                self.p_e = np.clip(
                    (factor * self.p_e) / (factor * self.p_e + (1 - self.p_e)),
                    0.1, 0.9
                )

        # Update observability model only where observation disagrees with model
        for pos, seen, p_s in queried:
            if abs((1.0 if seen else 0.0) - p_s) > 0.25:
                self._update(pos, seen)

        self.new_observations.clear()
        print(f"{self}: p_e = {self.p_e:.3f}, coverage = {coverage:.2f}")

    def __str__(self):
        return f"DiscreteBoundary(n={self.n})"

ObservabilityModels = [DiscreteBoundary(360)]


if __name__ == "__main__":
    model = DiscreteBoundary(36)
    pos = (1, 2)
    print(f"Observability at {pos} = {model.query(pos)}")