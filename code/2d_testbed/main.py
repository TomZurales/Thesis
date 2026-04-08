"""
2D Testbed Application

A simple 2D testbed for camera movement and obstacle interaction.
Features polar coordinate camera movement and interactive rectangle drawing.

Controls:
- Arrow Keys: Move camera (forward/backward, rotate left/right)
- Space: Increment run counter
- Right Click: Draw rectangles or remove existing ones
- ESC: Quit

The camera moves in polar coordinates (radius, angle) around a center point,
and collision detection prevents movement into obstacles.
"""

from game import create_game


def main():
    """
    Entry point for the 2D testbed application.
    Creates and runs the game instance.
    """
    print("HERE")
    game = create_game()
    game.run()


if __name__ == "__main__":
    main()
