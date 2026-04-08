"""
Renderer for the 2D testbed application.
Handles all drawing operations and visual presentation.
"""

import pygame
from typing import List, Tuple, Optional
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, BLACK, WHITE, RED, GREEN,
    DOT_RADIUS, OBSERVATION_DOT_RADIUS, FONT_SIZE, FPS
)


class Renderer:
    """
    Handles all rendering operations for the 2D testbed.
    Provides methods for drawing different game elements.
    """
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2D Testbed")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        
        # Center point for reference
        self.center_x = WINDOW_WIDTH // 2
        self.center_y = WINDOW_HEIGHT // 2
    
    def clear_screen(self):
        """Clear the screen with white background."""
        self.screen.fill(WHITE)
    
    def draw_center_dot(self):
        """Draw the black reference dot in the center of the screen."""
        pygame.draw.circle(self.screen, BLACK, (self.center_x, self.center_y), DOT_RADIUS)
    
    def draw_camera(self, screen_x: int, screen_y: int, color: Tuple[int, int, int] = RED):
        """
        Draw the camera dot at the specified screen coordinates with the given color.
        
        Args:
            screen_x: X coordinate on screen
            screen_y: Y coordinate on screen
            color: RGB color tuple for the camera dot
        """
        pygame.draw.circle(self.screen, color, (screen_x, screen_y), DOT_RADIUS)
    
    def draw_rectangles(self, rectangles: List[Tuple[int, int, int, int]]):
        """
        Draw all the obstacle rectangles.
        
        Args:
            rectangles: List of rectangles as (x, y, width, height) tuples
        """
        for rect in rectangles:
            pygame.draw.rect(self.screen, BLACK, rect)
    
    def draw_rectangle_being_drawn(self, rect: Optional[Tuple[int, int, int, int]]):
        """
        Draw the rectangle currently being drawn (as an outline).
        
        Args:
            rect: Rectangle as (x, y, width, height) tuple, or None if not drawing
        """
        if rect is not None:
            pygame.draw.rect(self.screen, BLACK, rect, 2)  # Draw outline only

    def draw_observations(self, observations: List[Tuple[Tuple[int, int], Tuple[int, int, int]]]):
        """Draw completed observations as small colored dots."""
        for (screen_x, screen_y), color in observations:
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), OBSERVATION_DOT_RADIUS)
    
    def draw_run_counter(self, run_number: int):
        """
        Draw the run counter in the upper left corner.
        
        Args:
            run_number: Current run number to display
        """
        run_text = self.font.render(f"Run: {run_number}", True, BLACK)
        self.screen.blit(run_text, (10, 10))
    
    def draw_camera_info(self, radius: float, angle: float):
        """
        Draw camera position information.
        
        Args:
            radius: Camera radius in polar coordinates
            angle: Camera angle in polar coordinates
        """
        info_text = self.font.render(f"Camera: r={radius:.1f}, θ={angle:.1f}°", True, BLACK)
        self.screen.blit(info_text, (10, 50))
    
    def draw_instructions(self):
        """Draw control instructions on screen."""
        instructions = [
            "Arrow Keys: Move camera",
            "Space: Increment run",
            "Right Click: Draw/Remove rectangles",
            "ESC: Quit"
        ]
        
        y_offset = WINDOW_HEIGHT - len(instructions) * 25 - 10
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 24).render(instruction, True, BLACK)
            self.screen.blit(text, (10, y_offset + i * 25))
    
    def present(self):
        """Present the rendered frame to the screen."""
        pygame.display.flip()
    
    def tick(self) -> int:
        """
        Tick the clock and return the time delta.
        
        Returns:
            Time elapsed in milliseconds since last tick
        """
        return self.clock.tick(FPS)
    
    def render_frame(self, 
                    camera_pos: Tuple[int, int],
                    camera_color: Tuple[int, int, int],
                    rectangles: List[Tuple[int, int, int, int]], 
                    drawing_rect: Optional[Tuple[int, int, int, int]], 
                    run_number: int,
                    show_instructions: bool = False,
                    observations: Optional[List[Tuple[Tuple[int, int], Tuple[int, int, int]]]] = None):
        """
        Render a complete frame with all game elements.
        
        Args:
            camera_pos: Camera screen coordinates (x, y)
            camera_color: RGB color tuple for the camera dot
            rectangles: List of obstacle rectangles
            drawing_rect: Rectangle currently being drawn, or None
            run_number: Current run number
            show_instructions: Whether to show control instructions
        """
        self.clear_screen()
        self.draw_center_dot()
        self.draw_rectangles(rectangles)
        self.draw_rectangle_being_drawn(drawing_rect)

        if observations:
            self.draw_observations(observations)

        self.draw_camera(*camera_pos, camera_color)
        self.draw_run_counter(run_number)
        
        if show_instructions:
            self.draw_instructions()
        
        self.present()