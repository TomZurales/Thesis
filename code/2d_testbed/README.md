# 2D Testbed Application

A clean, modular 2D testbed for camera movement and obstacle interaction using pygame.

## Features

- **Polar coordinate camera movement** around a central reference point
- **Interactive obstacle drawing** with right-click drag
- **Line-of-sight visualization** - camera changes color based on visibility to center
- **Observability tracking** - automatic logging of camera observations and day completions
- **Collision detection** preventing camera movement through obstacles  
- **Real-time visual feedback** with camera position display
- **Clean modular architecture** for easy extension and maintenance

## Controls

| Input | Action |
|-------|--------|
| ↑ Arrow Key | Move camera forward (decrease radius) |
| ↓ Arrow Key | Move camera backward (increase radius) |  
| ← Arrow Key | Rotate camera left (counter-clockwise) |
| → Arrow Key | Rotate camera right (clockwise) |
| Right Click + Drag | Draw new rectangle obstacle |
| Right Click on Rectangle | Remove existing rectangle |
| Space | Increment run counter |
| ESC | Quit application |

## Camera Color Indicators

| Color | Meaning |
|-------|--------|
| 🟢 Green | Clear line of sight to center dot |
| 🔴 Red | Line of sight blocked by obstacle |

## Architecture

The application follows a clean separation of concerns with the following modules:

### Core Modules

- **`main.py`** - Entry point and application documentation
- **`game.py`** - Main game coordinator and loop management
- **`constants.py`** - Centralized configuration and settings

### Subsystem Modules

- **`camera.py`** - Camera position management in polar coordinates
- **`rectangle_system.py`** - Obstacle creation, removal, and management
- **`input_handler.py`** - Keyboard and mouse input processing
- **`renderer.py`** - All drawing and visual presentation

### Key Design Principles

1. **Single Responsibility** - Each module handles one specific concern
2. **Dependency Injection** - Components receive their dependencies explicitly  
3. **State Encapsulation** - No global variables; state is properly managed within classes
4. **Clean Interfaces** - Simple, well-defined APIs between components
5. **Type Hints** - Comprehensive type annotations for better code documentation

## Running the Application

```bash
cd /path/to/2d_testbed
python main.py
```

## Code Structure

```
2d_testbed/
├── main.py              # Entry point with documentation
├── game.py              # Main game coordination 
├── constants.py         # Configuration and settings
├── camera.py            # Camera movement and collision
├── rectangle_system.py  # Obstacle management
├── input_handler.py     # Input event processing  
├── renderer.py          # Drawing and presentation
├── geometry_utils.py    # Ray casting and collision utilities
├── observability_model.py # Observability tracking and logging
├── config_manager.py    # Configuration system (extension example)
├── extended_cameras.py  # Advanced camera modes (extension example)  
└── README.md           # This documentation
```

## Extension Points

The modular design makes it easy to extend functionality:

- **Add new input methods** by extending `InputHandler`
- **Create different camera behaviors** by subclassing `Camera`
- **Implement new obstacle types** by extending `RectangleSystem`
- **Add visual effects** by enhancing `Renderer`
- **Introduce new game modes** by modifying `Game`

### Extension Examples

The project includes example extensions that demonstrate the improved architecture:

- **`config_manager.py`** - Configuration system with file persistence
- **`extended_cameras.py`** - Advanced camera modes (smooth movement, auto-orbit, constraints)

These demonstrate how the clean interfaces and separation of concerns make it trivial to add sophisticated new features without modifying existing code.

## Requirements

- Python 3.7+
- pygame

Install dependencies:
```bash
pip install pygame
```

## Refactoring Benefits

This refactor transformed a monolithic 200+ line file with global state into a clean, modular architecture with these improvements:

### Before (Original):
- ❌ Heavy use of global variables mixed with class state
- ❌ Single 200-line file handling all responsibilities  
- ❌ Poor separation between input, logic, and rendering
- ❌ Difficult to test individual components
- ❌ Hard to extend without modifying existing code

### After (Refactored):
- ✅ **Zero global variables** - all state properly encapsulated
- ✅ **6 focused modules** with single responsibilities
- ✅ **Clean interfaces** between all components
- ✅ **Easy to test** - each module can be tested independently
- ✅ **Highly extensible** - new features added without touching existing code
- ✅ **Type-safe** - comprehensive type hints throughout
- ✅ **Self-documenting** - clear module purposes and APIs

The refactored code is significantly more maintainable, testable, and ready for future development.