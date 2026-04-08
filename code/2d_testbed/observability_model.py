import math
from typing import List, Tuple


Observation = Tuple[Tuple[float, float], bool]


class obsability_model:
    MIN_DIST = 100.0  # Minimum distance threshold for adding observations
    MERGE_ANGLE_DEGREES = 30.0  # Angular window for resolving conflicting observations
    
    def __init__(self):
        # Observations collected during the current run/day.
        self.observations: List[Observation] = []
        # Persisted observations shown on screen after runs are completed.
        self.completed_observations: List[Observation] = []
        self.last_position: Tuple[float, float] | None = None

    def _polar_distance(self, pos1, pos2) -> float:
        """Calculate distance between two polar coordinate points (r, theta)."""
        r1, theta1 = pos1
        r2, theta2 = pos2
        
        theta1_rad = math.radians(theta1)
        theta2_rad = math.radians(theta2)
        return math.sqrt(r1**2 + r2**2 - 2 * r1 * r2 * math.cos(theta2_rad - theta1_rad))

    def _angle_distance(self, angle_a: float, angle_b: float) -> float:
        """Return the smallest absolute angular difference in degrees."""
        return abs((angle_a - angle_b + 180.0) % 360.0 - 180.0)

    def _should_remove_stored_observation(
        self,
        new_observation: Observation,
        stored_observation: Observation,
    ) -> bool:
        """Determine whether a stored observation conflicts with a new one."""
        (new_radius, new_angle), new_seen = new_observation
        (stored_radius, stored_angle), stored_seen = stored_observation

        is_within_angle = self._angle_distance(new_angle, stored_angle) <= self.MERGE_ANGLE_DEGREES
        if not is_within_angle:
            return False

        if new_seen:
            return (not stored_seen) and stored_radius < new_radius

        return stored_seen and stored_radius > new_radius

    def observe(self, cam_position, seen: bool):
        """Record an observation for the current collection period if the camera moved far enough."""
        should_add = True
        if self.last_position is not None:
            distance = self._polar_distance(cam_position, self.last_position)
            should_add = distance > self.MIN_DIST
        
        if should_add:
            self.observations.append((cam_position, seen))
            self.last_position = cam_position
            if seen:
                print(f"Camera at {cam_position} can see the target.")
            else:
                print(f"Camera at {cam_position} cannot see the target.")

    def get_completed_observations(self) -> List[Observation]:
        """Return all stored observations that should currently be shown on screen."""
        return list(self.completed_observations)
    
    def complete_day(self):
        """Merge new observations into the stored set using the observability pruning rules."""
        merged_observations = list(self.completed_observations)
        removed_count = 0

        for new_observation in self.observations:
            before_count = len(merged_observations)
            merged_observations = [
                stored_observation
                for stored_observation in merged_observations
                if not self._should_remove_stored_observation(new_observation, stored_observation)
            ]
            removed_count += before_count - len(merged_observations)
            merged_observations.append(new_observation)

        day_count = len(self.observations)
        self.completed_observations = merged_observations
        self.observations = []
        self.last_position = None

        print(
            f"Day completed. Merged {day_count} new observations, "
            f"removed {removed_count} conflicting stored observations, "
            f"now showing {len(self.completed_observations)} total."
        )