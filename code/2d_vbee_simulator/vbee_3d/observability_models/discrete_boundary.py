import math

def clamp(value, minmax_value):
    return max(-minmax_value, min(minmax_value, value))

def map_value(value, from_min, from_max, to_min, to_max):
    if from_max == from_min:
        return to_min
    return to_min + (to_max - to_min) * ((value - from_min) / (from_max - from_min))

ICOS_CENTERS = [
    [-0.1875924741, 0.7946544723, -0.5773502692],
    [0.4911234732, 0.7946544723, 0.3568220898],
    [-0.6070619982, 0.7946544723, -0.0000000000],
    [0.4911234732, 0.7946544723, -0.3568220898],
    [-0.1875924741, 0.7946544723, 0.5773502692],
    [-0.9822469464, 0.1875924741, -0.0000000000],
    [-0.3035309991, 0.1875924741, 0.9341723590],
    [0.7946544723, 0.1875924741, -0.5773502692],
    [-0.3035309991, 0.1875924741, -0.9341723590],
    [0.7946544723, 0.1875924741, 0.5773502692],
    [-0.7946544723, -0.1875924741, -0.5773502692],
    [0.3035309991, -0.1875924741, 0.9341723590],
    [-0.7946544723, -0.1875924741, 0.5773502692],
    [0.3035309991, -0.1875924741, -0.9341723590],
    [0.9822469464, -0.1875924741, 0.0000000000],
    [0.1875924741, -0.7946544723, -0.5773502692],
    [0.6070619982, -0.7946544723, 0.0000000000],
    [-0.4911234732, -0.7946544723, 0.3568220898],
    [-0.4911234732, -0.7946544723, -0.3568220898],
    [0.1875924741, -0.7946544723, 0.5773502692],
]

N = 20  # icosahedron face count
_BIN_VOL_COEFF = math.pi / 15  # (4π/20) / 3 = π/15


class DiscreteBoundary:
    def __init__(self, k: int = 5, ambiguous_range: float = 0.5):
        self.k = k
        self.ambiguous_range = ambiguous_range
        self.max_seen = [0] * N
        self.min_unseen = [float('inf')] * N
        self.bin_observabilities = [0] * N
        self.bin_ambiguous = [k] * N

    def query(self, position: tuple[float, float, float]) -> float:
        x, y, z = position
        r = (x**2 + y**2 + z**2)**0.5
        b = self._select_bin(position)
        if r <= self.max_seen[b]:
            if r < self.min_unseen[b]:
                return 1.0
            else:
                return map_value(self.bin_ambiguous[b], 0, 2 * self.k, 0.5 - (self.ambiguous_range / 2), 0.5 + (self.ambiguous_range / 2))
        else:
            return 0.0

    def update(self, observation: tuple[float, float, float, bool]) -> float:
        x, y, z, obs = observation
        r = (x**2 + y**2 + z**2)**0.5
        b = self._select_bin((x, y, z))

        updated = False

        if obs:
            if r > self.max_seen[b]:
                self.max_seen[b] = r
                updated = True
        else:
            if r < self.min_unseen[b]:
                self.min_unseen[b] = r
                updated = True

        if r <= self.max_seen[b] and r >= self.min_unseen[b]:
            if obs:
                self.bin_ambiguous[b] = min(2 * self.k, self.bin_ambiguous[b] + 1)
            else:
                self.bin_ambiguous[b] = max(0, self.bin_ambiguous[b] - 1)
            updated = True

        if updated:
            if self.min_unseen[b] < self.max_seen[b]:
                s1_vol = _BIN_VOL_COEFF * (self.min_unseen[b] ** 3)
                s2_vol = _BIN_VOL_COEFF * (self.max_seen[b] ** 3) - s1_vol
                self.bin_observabilities[b] = s1_vol + (map_value(self.bin_ambiguous[b], 0, 2 * self.k, 0.5 - (self.ambiguous_range / 2), 0.5 + (self.ambiguous_range / 2)) * s2_vol)
            else:
                self.bin_observabilities[b] = _BIN_VOL_COEFF * (self.max_seen[b] ** 3)

        return sum(self.bin_observabilities)

    def getObservability(self) -> float:
        return sum(self.bin_observabilities)

    def _select_bin(self, position: tuple[float, float, float]) -> int:
        x, y, z = position
        r = (x**2 + y**2 + z**2)**0.5
        if r == 0:
            return 0
        nx, ny, nz = x / r, y / r, z / r
        return max(range(N), key=lambda i: nx * ICOS_CENTERS[i][0] + ny * ICOS_CENTERS[i][1] + nz * ICOS_CENTERS[i][2])
