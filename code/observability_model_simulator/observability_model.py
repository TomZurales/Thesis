import random
import numpy as np
from scipy.spatial import ConvexHull, Delaunay, cKDTree
from utility import cartesian_to_polar
from dataclasses import dataclass

@dataclass
class Bin:
    center: float
    positive: float = -1.0
    negative: float = float('inf')

class ObservabilityModel:
    def __init__(self):
        self.all_observations: list[tuple[tuple[int, int], bool]] = []
        self.observations: list[tuple[tuple[int, int], bool]] = []
    
    def add_observation(self, position: tuple[int, int], seen: bool):
        self.all_observations.append((position, seen))
        self._update(position, seen)

    def _update(self, position: tuple[int, int], seen: bool):
        pass

    def query(self, position: tuple[int, int]) -> float:
        pass

    def set_target(self, position: tuple[int, int]):
        self.goal = position

    def __str__(self):
        pass

class RandomObservabilityModel(ObservabilityModel):
    def query(self, position: tuple[int, int]) -> float:
        return random.random()
    
    def __str__(self):
        return "Random"


class KNNObservabilityModel(ObservabilityModel):
    def __init__(self, k: int = 3):
        super().__init__()
        self.k = k
        self._tree: cKDTree | None = None
        self._seen: np.ndarray = np.array([], dtype=bool)

    def _update(self, position: tuple[int, int], seen: bool):
        # KNN model uses all observations for building the tree
        self.observations.append((position, seen))

        positions = np.array([pos for pos, _ in self.observations])
        self._seen = np.array([seen for _, seen in self.observations], dtype=bool)
        self._tree = cKDTree(positions)

    def query(self, position: tuple[int, int]) -> float:
        if self._tree is None:
            return 0.5
        k = min(self.k, len(self.observations))
        _, indices = self._tree.query(position, k=k)
        return float(self._seen[indices].mean())
    
    def __str__(self):
        return f"KNN(k={self.k})"
    
class DiscreteBoundary(ObservabilityModel):
    def __init__(self, n: int):
        super().__init__()
        self.n = n
        self.positive_boundaries = [-1 for _ in range(n)]
        self.negative_boundaries = [np.inf for _ in range(n)]
        self.bin_centers = [2 * np.pi * i / n for i in range(n)]
        self.bin_centers.append(2 * np.pi)

    def _get_bin_index(self, theta: float) -> int:
        # Find the bin index for which theta theta is closest to the bin center
        diffs = [abs(theta - center) for center in self.bin_centers]
        bin = int(np.argmin(diffs))
        if bin == self.n:
            bin = 0
        return bin

    def _update(self, position: tuple[int, int], seen: bool):        
        r, theta = cartesian_to_polar(position[0], position[1], relative_to=self.goal)
        # find which discrete angle bin this observation falls into
        bin_index = self._get_bin_index(theta)
        if seen and r > self.positive_boundaries[bin_index]:
            self.positive_boundaries[bin_index] = r
            # Set negative boundary to positive boundary if it was previously closer
            if self.negative_boundaries[bin_index] < self.positive_boundaries[bin_index]:
                self.negative_boundaries[bin_index] = r
        elif not seen and r < self.negative_boundaries[bin_index]:
            self.negative_boundaries[bin_index] = r
            if self.positive_boundaries[bin_index] > self.negative_boundaries[bin_index]:
                self.positive_boundaries[bin_index] = r


    def query(self, position: tuple[int, int]) -> float:
        r, theta = cartesian_to_polar(position[0], position[1], relative_to=self.goal)
        # find which discrete angle bin this query falls into
        bin_index = self._get_bin_index(theta)

        if r < self.positive_boundaries[bin_index]:
            return 1.0
        if r > self.negative_boundaries[bin_index]:
            return 0.0
        
        # If we fall between the positive / negative boundaries for this bin, interpolate
        pos = self.positive_boundaries[bin_index]
        neg = self.negative_boundaries[bin_index]
        if pos == -1 or neg == np.inf:
            # one of the boundaries is undefined, fall back to 0.5
            return 0.5
        return float((neg - r) / (neg - pos))

    
    def __str__(self):
        return f"DiscreteBoundary(n={self.n})"
    
class LearnedBoundary(ObservabilityModel):
    def __init__(self):
        super().__init__()
        self.boundaries: list[Bin] = []

    def _get_bin_index(self, theta: float) -> int:
        if not self.boundaries:
            return -1
        # Find the bin index for which theta is closest, accounting for the 0/2π wrap-around
        diffs = [min(d := abs(theta - b.center) % (2 * np.pi), (2 * np.pi) - d) for b in self.boundaries]
        bin = int(np.argmin(diffs))
        if bin == len(self.boundaries):
            bin = 0
        return bin

    def _update(self, position: tuple[int, int], seen: bool):
        r, theta = cartesian_to_polar(position[0], position[1], relative_to=self.goal)
        if len(self.boundaries) == 0:
            # first observation, initialize the first bin
            self.boundaries.append(Bin(
                center=theta,
                positive=r if seen else -1.0,
                negative=r if not seen else np.inf,
            ))
            print(f"NEW BIN {theta}")
            return

        # Find the bin that this observation falls into
        bin_index = self._get_bin_index(theta)
        b = self.boundaries[bin_index]

        # First, check for disagreement. Create a new bin if this observation disagrees with the current state
        # If we see the point, we have a negative boundary established, and we are in the region outside the current negative boundary OR
        # we don't see the point, we have a positive boundary established, and we are in the region inside the current positive boundary but outside the negative boundary
        if (seen and b.negative != np.inf and r > b.negative) or (not seen and b.positive != -1.0 and r < b.positive):
            # Check if we are near a bin boundary. If we are close to the edge of an existing bin,
            # we may want to slide the bin edge rather than create a new bin right at the
            # discontinuity between bins
            dist = self.dist_to_border(theta)
            if abs(dist) < 0.1 and abs(dist) > 0.01:  # near a border, slide the bin center rather than add a new bin
                b.center = b.center + dist
                print(f"SLID BIN {bin_index} TO {b.center}")
                return

            # Place the new bin so its border with the conflicting bin falls at
            # theta, making the observation lie right at the edge of the new bin.
            # border = midpoint(b.center, c_new) = theta  =>  c_new = 2θ - b.center
            c_new = (2 * theta - b.center) % (2 * np.pi)
            self.boundaries.append(Bin(
                center=c_new,
                positive=r if seen else -1.0,
                negative=r if not seen else np.inf,
            ))
            print(f"NEW BIN center={c_new:.4f} (border at theta={theta:.4f})")
            return

        if seen and r > b.positive:
            b.positive = r
        elif not seen and r < b.negative:
            b.negative = r

    def query(self, position: tuple[int, int]) -> float:
        r, theta = cartesian_to_polar(position[0], position[1], relative_to=self.goal)
        # find which discrete angle bin this query falls into
        bin_index = self._get_bin_index(theta)

        if bin_index == -1:
            return 0.5
        b = self.boundaries[bin_index]
        if r < b.positive:
            return 1.0
        if r > b.negative:
            return 0.0

        return 0.5

    def dist_to_border(self, theta: float) -> float:
        """Signed angular distance from theta to the nearest bin border.

        Bin borders are the angular midpoints between adjacent bin centers
        (sorted by angle, with wrap-around between the last and first bin).

        Sign convention: positive when the nearest border is to the left of
        theta (i.e. at a smaller angle in the short-arc sense), negative when
        to the right.  Returns inf when fewer than two bins exist.
        """
        if len(self.boundaries) < 2:
            return float('inf')

        centers = sorted(b.center for b in self.boundaries)
        n = len(centers)

        # Borders are midpoints between consecutive centers (including wrap-around)
        borders = []
        for i in range(n):
            a = centers[i]
            c = centers[(i + 1) % n]
            delta = (c - a) % (2 * np.pi)
            borders.append((a + delta / 2) % (2 * np.pi))

        # Find the border with minimum |distance|; return signed distance.
        # d = (theta - border) wrapped to (-π, π]: positive → border is to the
        # left (theta is CCW of border), negative → border is to the right.
        best = float('inf')
        for border in borders:
            d = (theta - border) % (2 * np.pi)
            if d > np.pi:
                d -= 2 * np.pi
            if abs(d) < abs(best):
                best = d
        return best

    def __str__(self):
        return f"LearnedBoundary"

class AdjustableDiscreteBoundaryObservabilityModel(ObservabilityModel):
    """Fixed n bins like DiscreteBoundary, but when a contradictory observation
    arrives the nearest bin center (in theta) slides to the observation's theta
    — the minimum move that gives it sole ownership of this angle — and its
    boundaries are reset to reflect only the new observation.  Normal (non-
    contradictory) observations update the bin's r boundaries in place."""

    def __init__(self, n: int = 36):
        super().__init__()
        self.n = n
        self.positive_boundaries = [-1.0] * n
        self.negative_boundaries = [np.inf] * n
        self.bin_centers = np.array([2 * np.pi * i / n for i in range(n)])

    def _get_bin_index(self, theta: float) -> int:
        d = np.abs(theta - self.bin_centers) % (2 * np.pi)
        d = np.minimum(d, 2 * np.pi - d)
        return int(np.argmin(d))

    def _contradicts(self, i: int, r: float, seen: bool) -> bool:
        if seen:
            return self.negative_boundaries[i] != np.inf and r > self.negative_boundaries[i]
        else:
            return self.positive_boundaries[i] != -1.0 and r < self.positive_boundaries[i]

    def _update(self, position: tuple[int, int], seen: bool):
        r, theta = cartesian_to_polar(position[0], position[1], relative_to=self.goal)
        i = self._get_bin_index(theta)

        if self._contradicts(i, r, seen):
            # Slide the bin center to this theta (minimum move to resolve the contradiction)
            # and reset its boundaries so only this observation is represented
            self.bin_centers[i] = theta
            self.positive_boundaries[i] = r if seen else -1.0
            self.negative_boundaries[i] = r if not seen else np.inf
        else:
            if seen and r > self.positive_boundaries[i]:
                self.positive_boundaries[i] = r
            elif not seen and r < self.negative_boundaries[i]:
                self.negative_boundaries[i] = r

    def query(self, position: tuple[int, int]) -> float:
        r, theta = cartesian_to_polar(position[0], position[1], relative_to=self.goal)
        i = self._get_bin_index(theta)
        if r < self.positive_boundaries[i]:
            return 1.0
        if r > self.negative_boundaries[i]:
            return 0.0
        pos = self.positive_boundaries[i]
        neg = self.negative_boundaries[i]
        if pos == -1.0 or neg == np.inf:
            return 0.5
        return float((neg - r) / (neg - pos))

    def __str__(self):
        return f"AdjustableDiscreteBoundary(n={self.n})"


class PinchedHullObservabilityModel(ObservabilityModel):
    def __init__(self):
        super().__init__()

    def _update(self, position: tuple[int, int], seen: bool):
        pass

    def query(self, position: tuple[int, int]) -> float:
        return 0.5

    def __str__(self):
        return f"PinchedHull"
    
class ConvexHullObservabilityModel(ObservabilityModel):
    def __init__(self):
        super().__init__()
        self._delaunay: Delaunay | None = None

    def _rebuild_delaunay(self):
        try:
            self._delaunay = Delaunay(np.array(self.observations + [self.goal], dtype=float))
        except Exception:
            self._delaunay = None  # Degenerate (e.g., collinear points)

    def _update(self, position: tuple[int, int], seen: bool):
        if not seen:
            return

        # We need 3 points (including the goal point) to form a convex hull
        if len(self.observations) < 2 or not hasattr(self, 'target'):
            self.observations.append(position)
            self._rebuild_delaunay()
            return

        # If position is already inside the current hull, discard it
        if self._delaunay is not None:
            if self._delaunay.find_simplex(np.array(position, dtype=float)) >= 0:
                return

        # Add the new point and rebuild the hull
        self.observations.append(position)
        all_points = np.array(self.observations + [self.goal], dtype=float)

        try:
            hull = ConvexHull(all_points)
            # Keep only observations that sit on the hull boundary; drop interior points
            hull_vertices = set(hull.vertices)
            self.observations = [
                self.observations[i]
                for i in range(len(self.observations))
                if i in hull_vertices
            ]
        except Exception:
            pass  # Hull computation failed (e.g., all points collinear); keep all

        self._rebuild_delaunay()

    def query(self, position: tuple[int, int]) -> float:
        if self._delaunay is None:
            return 0.5
        inside = self._delaunay.find_simplex(np.array(position, dtype=float)) >= 0
        return 1.0 if inside else 0.0


    def __str__(self):
        return "Convex Hull"


class ConcaveHullObservabilityModel(ObservabilityModel):
    """Delaunay triangulation of positive observations, with triangles that
    contain any negative observation removed.  Query returns 1.0 if the point
    lies in any surviving triangle, 0.0 otherwise."""

    def __init__(self):
        super().__init__()
        self.positive_observations: list[tuple[int, int]] = []
        self.negative_observations: list[tuple[int, int]] = []
        self._triangles: np.ndarray | None = None  # shape (n, 3, 2)

    def _rebuild(self):
        points = self.positive_observations + ([self.goal] if hasattr(self, 'target') else [])
        if len(points) < 3:
            self._triangles = None
            return
        pts = np.array(points, dtype=float)
        try:
            tri = Delaunay(pts)
        except Exception:
            self._triangles = None
            return

        triangles = pts[tri.simplices]  # shape (n, 3, 2)

        if self.negative_observations:
            neg = np.array(self.negative_observations, dtype=float)  # shape (m, 2)
            keep = ~self._triangles_contain_any(triangles, neg)
            triangles = triangles[keep]

        self._triangles = triangles if len(triangles) > 0 else None

    @staticmethod
    def _triangles_contain_any(triangles: np.ndarray, points: np.ndarray) -> np.ndarray:
        """Return bool array of shape (n,): True if triangle i contains at least one point.

        Uses barycentric coordinates.  triangles: (n,3,2), points: (m,2).
        """
        a = triangles[:, 0, :]   # (n, 2)
        b = triangles[:, 1, :]
        c = triangles[:, 2, :]
        v0 = c - a               # (n, 2)
        v1 = b - a               # (n, 2)

        dot00 = np.sum(v0 * v0, axis=1)   # (n,)
        dot01 = np.sum(v0 * v1, axis=1)
        dot11 = np.sum(v1 * v1, axis=1)
        denom = dot00 * dot11 - dot01 ** 2  # (n,)
        valid = denom != 0

        hit = np.zeros(len(triangles), dtype=bool)
        for p in points:
            v2 = p - a                              # (n, 2)
            dot02 = np.sum(v2 * v0, axis=1)         # (n,)
            dot12 = np.sum(v2 * v1, axis=1)
            u = np.where(valid, (dot11 * dot02 - dot01 * dot12) / np.where(valid, denom, 1), -1)
            v = np.where(valid, (dot00 * dot12 - dot01 * dot02) / np.where(valid, denom, 1), -1)
            hit |= (u >= 0) & (v >= 0) & (u + v <= 1)
        return hit

    def _update(self, position: tuple[int, int], seen: bool):
        if seen:
            self.positive_observations.append(position)
        else:
            self.negative_observations.append(position)
        self._rebuild()

    def query(self, position: tuple[int, int]) -> float:
        if self._triangles is None:
            return 0.5
        p = np.array(position, dtype=float)
        a = self._triangles[:, 0, :]
        b = self._triangles[:, 1, :]
        c = self._triangles[:, 2, :]
        v0 = c - a
        v1 = b - a
        v2 = p - a
        dot00 = np.sum(v0 * v0, axis=1)
        dot01 = np.sum(v0 * v1, axis=1)
        dot11 = np.sum(v1 * v1, axis=1)
        dot02 = np.sum(v2 * v0, axis=1)
        dot12 = np.sum(v2 * v1, axis=1)
        denom = dot00 * dot11 - dot01 ** 2
        valid = denom != 0
        u = np.where(valid, (dot11 * dot02 - dot01 * dot12) / np.where(valid, denom, 1), -1)
        v = np.where(valid, (dot00 * dot12 - dot01 * dot02) / np.where(valid, denom, 1), -1)
        return 1.0 if np.any((u >= 0) & (v >= 0) & (u + v <= 1)) else 0.0

    def __str__(self):
        return "Concave Hull"


ObservabilityModels = [RandomObservabilityModel(), KNNObservabilityModel(10), KNNObservabilityModel(1), DiscreteBoundary(144), LearnedBoundary(), AdjustableDiscreteBoundaryObservabilityModel(36), PinchedHullObservabilityModel(), ConvexHullObservabilityModel(), ConcaveHullObservabilityModel()]


if __name__ == "__main__":
    model = RandomObservabilityModel()
    pos = (1, 2)
    print(f"Observability at {pos} = {model.query(pos)}")