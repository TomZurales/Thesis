"""
Rectangle system for managing drawable obstacles in the 2D testbed.
Handles creation, removal, and management of rectangular obstacles.
"""

from typing import List, Tuple, Optional
import pygame
from constants import MIN_RECTANGLE_SIZE


class RectangleSystem:
    """
    Manages a collection of rectangular obstacles that can be drawn and removed.
    Handles mouse interaction for creating and removing rectangles.
    """
    
    def __init__(self):
        self.rectangles: List[Tuple[int, int, int, int]] = []
        self.drawing_rect = False
        self.rect_start_pos: Optional[Tuple[int, int]] = None
        self.current_mouse_pos: Optional[Tuple[int, int]] = None
    
    def get_rectangles(self) -> List[Tuple[int, int, int, int]]:
        """Get a copy of all rectangles."""
        return self.rectangles.copy()
    
    def start_drawing_rectangle(self, start_pos: Tuple[int, int]):
        """
        Start drawing a new rectangle from the given position.
        
        Args:
            start_pos: Mouse position where drawing started (x, y)
        """
        self.drawing_rect = True
        self.rect_start_pos = start_pos
        self.current_mouse_pos = start_pos
    
    def update_drawing_rectangle(self, current_pos: Tuple[int, int]):
        """
        Update the current rectangle being drawn.
        
        Args:
            current_pos: Current mouse position (x, y)
        """
        if self.drawing_rect:
            self.current_mouse_pos = current_pos
    
    def finish_drawing_rectangle(self) -> bool:
        """
        Finish drawing the current rectangle and add it to the collection.
        
        Returns:
            True if rectangle was created successfully, False otherwise
        """
        if not self.drawing_rect or not self.rect_start_pos or not self.current_mouse_pos:
            self.drawing_rect = False
            self.rect_start_pos = None
            self.current_mouse_pos = None
            return False
        
        x1, y1 = self.rect_start_pos
        x2, y2 = self.current_mouse_pos
        
        # Ensure positive width/height
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # Only create if rectangle is large enough
        if width > MIN_RECTANGLE_SIZE and height > MIN_RECTANGLE_SIZE:
            self.rectangles.append((x, y, width, height))
            success = True
        else:
            success = False
        
        # Reset drawing state
        self.drawing_rect = False
        self.rect_start_pos = None
        self.current_mouse_pos = None
        
        return success
    
    def cancel_drawing_rectangle(self):
        """Cancel the current rectangle drawing operation."""
        self.drawing_rect = False
        self.rect_start_pos = None
        self.current_mouse_pos = None
    
    def remove_rectangle_at_position(self, pos: Tuple[int, int]) -> bool:
        """
        Remove a rectangle that contains the given position.
        
        Args:
            pos: Position to check (x, y)
        
        Returns:
            True if a rectangle was removed, False otherwise
        """
        x, y = pos
        for i, rect in enumerate(self.rectangles):
            rect_x, rect_y, rect_w, rect_h = rect
            if (rect_x <= x <= rect_x + rect_w and 
                rect_y <= y <= rect_y + rect_h):
                self.rectangles.pop(i)
                return True
        return False
    
    def get_current_drawing_rectangle(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the rectangle currently being drawn, if any.
        
        Returns:
            Rectangle as (x, y, width, height) tuple, or None if not drawing
        """
        if not self.drawing_rect or not self.rect_start_pos or not self.current_mouse_pos:
            return None
        
        x1, y1 = self.rect_start_pos
        x2, y2 = self.current_mouse_pos
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        return (x, y, width, height)
    
    def is_drawing(self) -> bool:
        """Check if currently drawing a rectangle."""
        return self.drawing_rect
    
    def clear_all_rectangles(self):
        """Remove all rectangles."""
        self.rectangles.clear()
        self.cancel_drawing_rectangle()