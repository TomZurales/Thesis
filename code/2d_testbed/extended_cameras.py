"""
Extended camera modes for the 2D testbed application.
Demonstrates how the refactored structure enables easy extension with new features.
"""

from camera import Camera
from typing import List, Tuple
from constants import CAMERA_MOVE_SPEED, CAMERA_ROTATION_SPEED
import math


class SmoothCamera(Camera):
    """
    Extended camera with smooth movement and momentum.
    Shows how the modular design enables easy feature extension.
    """
    
    def __init__(self, smoothing_factor: float = 0.1):
        super().__init__()
        self.smoothing_factor = smoothing_factor
        self.target_radius = self.radius
        self.target_angle = self.angle
        self.velocity_radius = 0.0
        self.velocity_angle = 0.0
        self.damping = 0.85  # Velocity damping factor
    
    def set_target_position(self, target_radius: float, target_angle: float):
        """Set target position for smooth movement."""
        self.target_radius = target_radius
        self.target_angle = target_angle
    
    def update_smooth_movement(self):
        """Update position with smooth interpolation toward target."""
        # Calculate velocity toward target
        radius_diff = self.target_radius - self.radius
        angle_diff = self.target_angle - self.angle
        
        # Handle angle wrapping
        if angle_diff > 180:
            angle_diff -= 360
        elif angle_diff < -180:
            angle_diff += 360
        
        # Apply smoothing
        self.velocity_radius += radius_diff * self.smoothing_factor
        self.velocity_angle += angle_diff * self.smoothing_factor
        
        # Apply damping
        self.velocity_radius *= self.damping
        self.velocity_angle *= self.damping
        
        # Update position
        self.radius += self.velocity_radius
        self.angle += self.velocity_angle
        
        # Normalize angle
        self.angle = self.angle % 360
    
    def move_forward_smooth(self, obstacles: List[Tuple[int, int, int, int]]) -> bool:
        """Move forward with smooth acceleration."""
        new_target = self.target_radius - CAMERA_MOVE_SPEED
        if self.can_move_to(new_target, self.target_angle, obstacles):
            self.target_radius = new_target
            return True
        return False
    
    def move_backward_smooth(self, obstacles: List[Tuple[int, int, int, int]]) -> bool:
        """Move backward with smooth acceleration."""
        new_target = self.target_radius + CAMERA_MOVE_SPEED
        if self.can_move_to(new_target, self.target_angle, obstacles):
            self.target_radius = new_target
            return True
        return False


class OrbitCamera(Camera):
    """
    Camera that automatically orbits around the center point.
    Another example of easy extension with the modular design.
    """
    
    def __init__(self, orbit_speed: float = 0.5, auto_orbit: bool = False):
        super().__init__()
        self.orbit_speed = orbit_speed
        self.auto_orbit = auto_orbit
        self.orbit_direction = 1  # 1 for clockwise, -1 for counter-clockwise
    
    def toggle_auto_orbit(self):
        """Toggle automatic orbiting on/off."""
        self.auto_orbit = not self.auto_orbit
    
    def set_orbit_direction(self, clockwise: bool = True):
        """Set orbit direction."""
        self.orbit_direction = 1 if clockwise else -1
    
    def update_orbit(self, obstacles: List[Tuple[int, int, int, int]]):
        """Update automatic orbital movement."""
        if self.auto_orbit:
            new_angle = self.angle + (self.orbit_speed * self.orbit_direction)
            if self.can_move_to(self.radius, new_angle, obstacles):
                self.angle = new_angle % 360


class ConstrainedCamera(Camera):
    """
    Camera with movement constraints and bounds.
    Shows how to add safety and boundary features to the base camera.
    """
    
    def __init__(self, min_radius: float = 50, max_radius: float = 400):
        super().__init__()
        self.min_radius = min_radius
        self.max_radius = max_radius
        self.forbidden_angles: List[Tuple[float, float]] = []  # (start, end) angle pairs
    
    def add_forbidden_angle_range(self, start_angle: float, end_angle: float):
        """Add an angle range that the camera cannot enter."""
        self.forbidden_angles.append((start_angle, end_angle))
    
    def clear_forbidden_angles(self):
        """Remove all forbidden angle ranges."""
        self.forbidden_angles.clear()
    
    def _is_angle_forbidden(self, angle: float) -> bool:
        """Check if an angle is in a forbidden range."""
        angle = angle % 360
        for start, end in self.forbidden_angles:
            if start <= end:
                if start <= angle <= end:
                    return True
            else:  # Range crosses 0/360 boundary
                if angle >= start or angle <= end:
                    return True
        return False
    
    def can_move_to(self, new_radius: float, new_angle: float, obstacles: List[Tuple[int, int, int, int]]) -> bool:
        """Extended collision check with radius and angle constraints."""
        # Check radius bounds
        if new_radius < self.min_radius or new_radius > self.max_radius:
            return False
        
        # Check forbidden angles
        if self._is_angle_forbidden(new_angle):
            return False
        
        # Check base collision detection
        return super().can_move_to(new_radius, new_angle, obstacles)


def create_smooth_camera() -> SmoothCamera:
    """Factory function for smooth camera."""
    return SmoothCamera()


def create_orbit_camera(auto_start: bool = False) -> OrbitCamera:
    """Factory function for orbit camera."""
    camera = OrbitCamera()
    if auto_start:
        camera.toggle_auto_orbit()
    return camera


def create_constrained_camera(min_r: float = 50, max_r: float = 400) -> ConstrainedCamera:
    """Factory function for constrained camera."""
    return ConstrainedCamera(min_r, max_r)