"""
Camera class for 2D testbed application.
Handles camera position in polar coordinates and movement logic.
"""

from math import cos, sin, radians
from typing import Tuple, List
from constants import (
    START_CAM_RADIUS, START_CAM_ANGLE,
    MIN_CAM_RADIUS, MAX_CAM_RADIUS,
    CAMERA_MOVE_SPEED, CAMERA_ROTATION_SPEED,
    WINDOW_WIDTH, WINDOW_HEIGHT, DOT_RADIUS
)


class Camera:
    """
    Camera class that manages position in polar coordinates (radius, angle).
    Provides collision-aware movement with obstacles.
    """
    
    def __init__(self):
        self.radius = self._clamp_radius(START_CAM_RADIUS)
        self.angle = self._normalize_angle(START_CAM_ANGLE)
        self.center_x = WINDOW_WIDTH // 2
        self.center_y = WINDOW_HEIGHT // 2

    def _clamp_radius(self, radius: float) -> float:
        """Clamp the camera radius to the allowed range."""
        return max(MIN_CAM_RADIUS, min(MAX_CAM_RADIUS, radius))

    def _normalize_angle(self, angle: float) -> float:
        """Keep the angle in the range [0, 360)."""
        return angle % 360
    
    @property
    def position(self) -> Tuple[float, float]:
        """Get camera position as (radius, angle) tuple."""
        return (self.radius, self.angle)
    
    @position.setter
    def position(self, pos: Tuple[float, float]):
        """Set camera position from (radius, angle) tuple."""
        radius, angle = pos
        self.radius = self._clamp_radius(radius)
        self.angle = self._normalize_angle(angle)
    
    def get_screen_coordinates(self) -> Tuple[int, int]:
        """Convert polar coordinates to screen coordinates."""
        x = self.radius * cos(radians(self.angle))
        y = self.radius * sin(radians(self.angle))
        screen_x = int(x + self.center_x)
        screen_y = int(y + self.center_y)
        return (screen_x, screen_y)
    
    def get_coordinates_for_position(self, radius: float, angle: float) -> Tuple[int, int]:
        """Get screen coordinates for a specific polar position."""
        clamped_radius = self._clamp_radius(radius)
        normalized_angle = self._normalize_angle(angle)
        x = clamped_radius * cos(radians(normalized_angle))
        y = clamped_radius * sin(radians(normalized_angle))
        screen_x = int(x + self.center_x)
        screen_y = int(y + self.center_y)
        return (screen_x, screen_y)
    
    def can_move_to(self, new_radius: float, new_angle: float, obstacles: List[Tuple[int, int, int, int]]) -> bool:
        """
        Check if camera can move to new position without colliding with obstacles.
        
        Args:
            new_radius: New radius value
            new_angle: New angle value
            obstacles: List of rectangles (x, y, width, height)
        
        Returns:
            True if movement is possible, False if collision would occur
        """
        clamped_radius = self._clamp_radius(new_radius)
        normalized_angle = self._normalize_angle(new_angle)
        screen_x, screen_y = self.get_coordinates_for_position(clamped_radius, normalized_angle)
        
        for rect in obstacles:
            rect_x, rect_y, rect_w, rect_h = rect
            # Check if camera circle overlaps with rectangle using closest point method
            closest_x = max(rect_x, min(screen_x, rect_x + rect_w))
            closest_y = max(rect_y, min(screen_y, rect_y + rect_h))
            distance = ((screen_x - closest_x) ** 2 + (screen_y - closest_y) ** 2) ** 0.5
            if distance < DOT_RADIUS:
                return False
        return True
    
    def move_forward(self, obstacles: List[Tuple[int, int, int, int]]) -> bool:
        """
        Move camera forward (decrease radius) if possible.
        
        Args:
            obstacles: List of obstacle rectangles
        
        Returns:
            True if movement was successful, False if blocked
        """
        new_radius = self._clamp_radius(self.radius - CAMERA_MOVE_SPEED)
        if new_radius == self.radius:
            return False

        if self.can_move_to(new_radius, self.angle, obstacles):
            self.radius = new_radius
            return True
        return False
    
    def move_backward(self, obstacles: List[Tuple[int, int, int, int]]) -> bool:
        """
        Move camera backward (increase radius) if possible.
        
        Args:
            obstacles: List of obstacle rectangles
        
        Returns:
            True if movement was successful, False if blocked
        """
        new_radius = self._clamp_radius(self.radius + CAMERA_MOVE_SPEED)
        if new_radius == self.radius:
            return False

        if self.can_move_to(new_radius, self.angle, obstacles):
            self.radius = new_radius
            return True
        return False
    
    def rotate_left(self, obstacles: List[Tuple[int, int, int, int]]) -> bool:
        """
        Rotate camera left (decrease angle) if possible.
        
        Args:
            obstacles: List of obstacle rectangles
        
        Returns:
            True if rotation was successful, False if blocked
        """
        new_angle = self._normalize_angle(self.angle - CAMERA_ROTATION_SPEED)
        if self.can_move_to(self.radius, new_angle, obstacles):
            self.angle = new_angle
            return True
        return False
    
    def rotate_right(self, obstacles: List[Tuple[int, int, int, int]]) -> bool:
        """
        Rotate camera right (increase angle) if possible.
        
        Args:
            obstacles: List of obstacle rectangles
        
        Returns:
            True if rotation was successful, False if blocked
        """
        new_angle = self._normalize_angle(self.angle + CAMERA_ROTATION_SPEED)
        if self.can_move_to(self.radius, new_angle, obstacles):
            self.angle = new_angle
            return True
        return False