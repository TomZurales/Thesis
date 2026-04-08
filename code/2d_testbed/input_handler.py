"""
Input handler for the 2D testbed application.
Manages keyboard and mouse input events and converts them to game actions.
"""

import pygame
from typing import Dict
from constants import (
    KEY_MOVE_FORWARD, KEY_MOVE_BACKWARD, KEY_ROTATE_LEFT, KEY_ROTATE_RIGHT,
    KEY_INCREMENT_RUN, KEY_QUIT, MOUSE_RIGHT_BUTTON
)


class InputHandler:
    """
    Handles all input events and maintains input state.
    Separates raw input from game logic by providing clean action methods.
    """
    
    def __init__(self):
        # Movement state
        self.movement_state = {
            'moving_forward': False,
            'moving_backward': False,
            'rotating_left': False,
            'rotating_right': False
        }
        
        # Action flags (set once per frame)
        self.actions_this_frame = {
            'quit_requested': False,
            'increment_run': False,
            'right_click_press': False,
            'right_click_release': False,
            'mouse_motion': False
        }
        
        self.mouse_position = (0, 0)
    
    def handle_events(self, events):
        """
        Process pygame events and update input state.
        
        Args:
            events: List of pygame events from pygame.event.get()
        """
        # Reset frame actions
        self.actions_this_frame = {key: False for key in self.actions_this_frame}
        
        for event in events:
            if event.type == pygame.QUIT:
                self.actions_this_frame['quit_requested'] = True
                
            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event.key)
                
            elif event.type == pygame.KEYUP:
                self._handle_key_up(event.key)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == MOUSE_RIGHT_BUTTON:
                    self.actions_this_frame['right_click_press'] = True
                    self.mouse_position = event.pos
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == MOUSE_RIGHT_BUTTON:
                    self.actions_this_frame['right_click_release'] = True
                    
            elif event.type == pygame.MOUSEMOTION:
                self.actions_this_frame['mouse_motion'] = True
                self.mouse_position = event.pos
    
    def _handle_key_down(self, key):
        """Handle key press events."""
        if key == KEY_MOVE_FORWARD:
            self.movement_state['moving_forward'] = True
        elif key == KEY_MOVE_BACKWARD:
            self.movement_state['moving_backward'] = True
        elif key == KEY_ROTATE_LEFT:
            self.movement_state['rotating_left'] = True
        elif key == KEY_ROTATE_RIGHT:
            self.movement_state['rotating_right'] = True
        elif key == KEY_INCREMENT_RUN:
            self.actions_this_frame['increment_run'] = True
        elif key == KEY_QUIT:
            self.actions_this_frame['quit_requested'] = True
    
    def _handle_key_up(self, key):
        """Handle key release events."""
        if key == KEY_MOVE_FORWARD:
            self.movement_state['moving_forward'] = False
        elif key == KEY_MOVE_BACKWARD:
            self.movement_state['moving_backward'] = False
        elif key == KEY_ROTATE_LEFT:
            self.movement_state['rotating_left'] = False
        elif key == KEY_ROTATE_RIGHT:
            self.movement_state['rotating_right'] = False
    
    # Query methods for game logic
    
    def is_quit_requested(self) -> bool:
        """Check if quit was requested this frame."""
        return self.actions_this_frame['quit_requested']
    
    def is_increment_run_pressed(self) -> bool:
        """Check if increment run key was pressed this frame."""
        return self.actions_this_frame['increment_run']
    
    def is_moving_forward(self) -> bool:
        """Check if forward movement key is held down."""
        return self.movement_state['moving_forward']
    
    def is_moving_backward(self) -> bool:
        """Check if backward movement key is held down."""
        return self.movement_state['moving_backward']
    
    def is_rotating_left(self) -> bool:
        """Check if left rotation key is held down."""
        return self.movement_state['rotating_left']
    
    def is_rotating_right(self) -> bool:
        """Check if right rotation key is held down."""
        return self.movement_state['rotating_right']
    
    def is_right_click_pressed(self) -> bool:
        """Check if right mouse button was pressed this frame."""
        return self.actions_this_frame['right_click_press']
    
    def is_right_click_released(self) -> bool:
        """Check if right mouse button was released this frame."""
        return self.actions_this_frame['right_click_release']
    
    def is_mouse_moving(self) -> bool:
        """Check if mouse moved this frame."""
        return self.actions_this_frame['mouse_motion']
    
    def get_mouse_position(self) -> tuple:
        """Get current mouse position."""
        return self.mouse_position