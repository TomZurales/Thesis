"""
Main game coordinator for the 2D testbed application.
Integrates all subsystems and manages the main game loop.
"""

import pygame
import sys
from camera import Camera
from rectangle_system import RectangleSystem
from input_handler import InputHandler
from renderer import Renderer
from geometry_utils import has_clear_line_of_sight
from constants import RED, GREEN, WINDOW_WIDTH, WINDOW_HEIGHT
from observability_model import obsability_model


class Game:
    """
    Main game class that coordinates all subsystems.
    Manages the game state and main loop.
    """
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Initialize subsystems
        self.camera = Camera()
        self.rectangle_system = RectangleSystem()
        self.input_handler = InputHandler()
        self.renderer = Renderer()
        self.observability_model = obsability_model()
        
        # Game state
        self.running = True
        self.run_number = 0
        self.show_instructions = True  # Show instructions initially
    
    def handle_input(self):
        """Process input and update game state accordingly."""
        events = pygame.event.get()
        self.input_handler.handle_events(events)
        
        # Handle quit requests
        if self.input_handler.is_quit_requested():
            self.running = False
        
        # Handle run increment
        if self.input_handler.is_increment_run_pressed():
            self.run_number += 1
            self.observability_model.complete_day()
        
        # Handle camera movement
        obstacles = self.rectangle_system.get_rectangles()
        camera_moved = False
        
        if self.input_handler.is_moving_forward():
            if self.camera.move_forward(obstacles):
                camera_moved = True
        
        if self.input_handler.is_moving_backward():
            if self.camera.move_backward(obstacles):
                camera_moved = True
        
        if self.input_handler.is_rotating_left():
            if self.camera.rotate_left(obstacles):
                camera_moved = True
        
        if self.input_handler.is_rotating_right():
            if self.camera.rotate_right(obstacles):
                camera_moved = True
        
        # Call observe method if camera moved
        if camera_moved:
            camera_pos = self.camera.position
            can_see_center = self.get_camera_color() == GREEN
            self.observability_model.observe(camera_pos, can_see_center)
        
        # Handle rectangle drawing
        self._handle_rectangle_interaction()
    
    def _handle_rectangle_interaction(self):
        """Handle mouse interaction for rectangle drawing/removal."""
        if self.input_handler.is_right_click_pressed():
            mouse_pos = self.input_handler.get_mouse_position()
            
            # Try to remove existing rectangle first
            if not self.rectangle_system.remove_rectangle_at_position(mouse_pos):
                # If no rectangle was removed, start drawing a new one
                self.rectangle_system.start_drawing_rectangle(mouse_pos)
        
        elif self.input_handler.is_right_click_released():
            if self.rectangle_system.is_drawing():
                self.rectangle_system.finish_drawing_rectangle()
        
        elif self.input_handler.is_mouse_moving():
            if self.rectangle_system.is_drawing():
                mouse_pos = self.input_handler.get_mouse_position()
                self.rectangle_system.update_drawing_rectangle(mouse_pos)
    
    def update(self):
        """Update game state. Currently, most updates are handled in input processing."""
        # Hide instructions after first interaction
        if (self.input_handler.is_moving_forward() or 
            self.input_handler.is_moving_backward() or
            self.input_handler.is_rotating_left() or
            self.input_handler.is_rotating_right() or
            self.input_handler.is_right_click_pressed()):
            self.show_instructions = False
    
    def get_camera_color(self) -> tuple:
        """
        Determine camera color based on line of sight to center dot.
        
        Returns:
            GREEN if clear line of sight to center, RED if blocked
        """
        camera_screen_pos = self.camera.get_screen_coordinates()
        center_pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        obstacles = self.rectangle_system.get_rectangles()
        
        if has_clear_line_of_sight(camera_screen_pos, center_pos, obstacles):
            return GREEN
        else:
            return RED
    
    def render(self):
        """Render the current frame."""
        camera_screen_pos = self.camera.get_screen_coordinates()
        camera_color = self.get_camera_color()
        rectangles = self.rectangle_system.get_rectangles()
        drawing_rect = self.rectangle_system.get_current_drawing_rectangle()

        observation_points = []
        for (radius, angle), seen in self.observability_model.get_completed_observations():
            observation_points.append((
                self.camera.get_coordinates_for_position(radius, angle),
                GREEN if seen else RED,
            ))
        
        self.renderer.render_frame(
            camera_pos=camera_screen_pos,
            camera_color=camera_color,
            rectangles=rectangles,
            drawing_rect=drawing_rect,
            run_number=self.run_number,
            show_instructions=self.show_instructions,
            observations=observation_points
        )
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.renderer.tick()
        
        self.quit()
    
    def quit(self):
        """Clean shutdown of the game."""
        pygame.quit()
        sys.exit()


def create_game() -> Game:
    """
    Factory function to create a new game instance.
    
    Returns:
        A new Game instance ready to run
    """
    return Game()