"""
Geometry utilities for the 2D testbed application.
Provides ray casting and collision detection functions.
"""

from typing import List, Tuple


def line_intersects_rectangle(line_start: Tuple[float, float], 
                            line_end: Tuple[float, float], 
                            rect: Tuple[int, int, int, int]) -> bool:
    """
    Check if a line segment intersects with a rectangle.
    
    Args:
        line_start: Starting point of the line (x, y)
        line_end: Ending point of the line (x, y)
        rect: Rectangle as (x, y, width, height) tuple
    
    Returns:
        True if the line intersects the rectangle, False otherwise
    """
    rect_x, rect_y, rect_w, rect_h = rect
    
    # Rectangle corners
    rect_left = rect_x
    rect_right = rect_x + rect_w
    rect_top = rect_y
    rect_bottom = rect_y + rect_h
    
    # Check if line segment intersects any of the four rectangle edges
    edges = [
        ((rect_left, rect_top), (rect_right, rect_top)),      # Top edge
        ((rect_right, rect_top), (rect_right, rect_bottom)),  # Right edge
        ((rect_right, rect_bottom), (rect_left, rect_bottom)), # Bottom edge
        ((rect_left, rect_bottom), (rect_left, rect_top))     # Left edge
    ]
    
    for edge_start, edge_end in edges:
        if line_segments_intersect(line_start, line_end, edge_start, edge_end):
            return True
    
    return False


def line_segments_intersect(p1: Tuple[float, float], p2: Tuple[float, float],
                           p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
    """
    Check if two line segments intersect.
    
    Uses the parametric line intersection algorithm.
    
    Args:
        p1, p2: Endpoints of the first line segment
        p3, p4: Endpoints of the second line segment
    
    Returns:
        True if the line segments intersect, False otherwise
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    # Calculate direction vectors
    dx1 = x2 - x1
    dy1 = y2 - y1
    dx2 = x4 - x3
    dy2 = y4 - y3
    
    # Calculate the denominator for the parametric equations
    denominator = dx1 * dy2 - dy1 * dx2
    
    # Lines are parallel if denominator is zero
    if abs(denominator) < 1e-10:
        return False
    
    # Calculate parameters
    dx3 = x1 - x3
    dy3 = y1 - y3
    
    t = (dx2 * dy3 - dy2 * dx3) / denominator
    u = (dx1 * dy3 - dy1 * dx3) / denominator
    
    # Check if intersection point is within both line segments
    return 0 <= t <= 1 and 0 <= u <= 1


def has_clear_line_of_sight(start_pos: Tuple[float, float], 
                          end_pos: Tuple[float, float], 
                          obstacles: List[Tuple[int, int, int, int]]) -> bool:
    """
    Check if there's a clear line of sight between two points.
    
    Args:
        start_pos: Starting point (x, y)
        end_pos: Ending point (x, y)
        obstacles: List of obstacle rectangles as (x, y, width, height) tuples
    
    Returns:
        True if there's a clear line of sight, False if any obstacle blocks it
    """
    for obstacle in obstacles:
        if line_intersects_rectangle(start_pos, end_pos, obstacle):
            return False
    return True