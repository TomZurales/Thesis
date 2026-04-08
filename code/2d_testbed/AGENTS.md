# AGENTS.md — 2D Testbed Project Guide

## Purpose
This folder contains a **Python/Pygame 2D testbed** used in the VBEE master's thesis research.

The research goal is to study **observability**: defining the viewpoints from which a **3D map point is visible**. This app provides a simplified 2D environment for quickly testing ideas about:
- camera viewpoint placement,
- line-of-sight visibility,
- obstacle occlusion,
- and observation logging for observability models.

In short: **this is an experimental 2D sandbox for validating visibility / observability behavior before or alongside the larger thesis system**.

---

## Scope Within the Thesis Repository
The repository contains many C++/CMake and research components, but this subproject is specifically:
- **Path:** `code/2d_testbed/`
- **Language:** Python
- **Framework:** `pygame`
- **Role:** lightweight interactive prototype / testbed

When modifying this app, focus on the files in this folder unless a change explicitly needs integration with other thesis components.

---

## High-Level Behavior
The application simulates a camera moving around a central target in **polar coordinates** (`radius`, `angle`).

Users can:
- move the camera with arrow keys,
- draw or remove rectangular obstacles,
- test whether the camera has a clear line of sight to the center target,
- record observations about whether the target is visible from a given viewpoint.

This makes the app useful for iterating on observability logic and visibility heuristics.

---

## Project Structure

```text
code/2d_testbed/
├── AGENTS.md              # This file: AI/developer project guide
├── README.md              # Human-oriented overview and controls
├── main.py                # Entry point; creates and runs the game
├── game.py                # Main coordinator and game loop
├── constants.py           # Window, colors, and shared constants
├── camera.py              # Camera state and polar-coordinate movement
├── rectangle_system.py    # Obstacle creation/removal and drawing state
├── input_handler.py       # Keyboard and mouse input processing
├── renderer.py            # Rendering and on-screen visualization
├── geometry_utils.py      # Collision / line-of-sight helper functions
├── observability_model.py # Observation logging and visibility tracking
├── config_manager.py      # Optional configuration helper / extension point
└── extended_cameras.py    # Experimental/extended camera behaviors
```

---

## Responsibilities of the Main Modules

### `main.py`
- App entry point.
- Calls `create_game()` and starts the runtime loop.

### `game.py`
- Central orchestration layer.
- Owns the main subsystems:
  - `Camera`
  - `RectangleSystem`
  - `InputHandler`
  - `Renderer`
  - `obsability_model`
- Handles:
  - input processing,
  - camera movement,
  - rectangle interaction,
  - visibility checks,
  - rendering per frame.

### `camera.py`
- Encapsulates camera position and movement.
- Movement is based on **polar coordinates around the center point**.
- Should remain the main place for changes to viewpoint motion rules.

### `rectangle_system.py`
- Manages obstacles in the environment.
- Supports interactive creation/removal of rectangles.
- Main place for changing obstacle behavior.

### `geometry_utils.py`
- Contains geometric checks such as collision and line-of-sight logic.
- Main place for modifying visibility / occlusion computations.

### `observability_model.py`
- Logs observations of the form: viewpoint + whether the target is visible.
- Represents the core research-facing logic for the testbed.
- Best starting point when experimenting with observability metrics.

### `renderer.py`
- Draws the scene and user feedback.
- Camera color indicates visibility state (clear view vs occluded).

### `input_handler.py`
- Converts keyboard/mouse events into clean game actions.
- Best place to add new controls.

---

## Runtime Flow
1. `main.py` starts the app.
2. `game.py` initializes all subsystems.
3. The main loop repeatedly:
   - reads user input,
   - updates camera / obstacle state,
   - checks line of sight to the center target,
   - records observations when movement occurs,
   - renders the updated frame.

---

## Key Concepts for AI Agents

### Central research concept
The important domain concept is **observability of a target from a viewpoint**.

In this 2D proxy:
- the **camera** = candidate viewpoint,
- the **center point** = target/map point of interest,
- the **rectangles** = occluders/obstacles,
- the **visibility test** = whether the viewpoint can observe the target.

### Design intent
The code is intentionally modular and should stay that way. Prefer changes that preserve the separation between:
- input,
- simulation logic,
- geometry,
- rendering,
- observability logging.

---

## Modification Guidance
When changing the project, prefer the following mapping:

| Goal | Best file(s) to edit |
|---|---|
| Change controls or interaction | `input_handler.py`, `game.py` |
| Change camera motion model | `camera.py` |
| Change visibility / occlusion rules | `geometry_utils.py`, `observability_model.py` |
| Change obstacle behavior | `rectangle_system.py` |
| Change on-screen visuals | `renderer.py`, `constants.py` |
| Change app startup or wiring | `main.py`, `game.py` |

---

## How to Run
From the repository root:

```bash
cd code/2d_testbed
python main.py
```

The workspace also appears to use a local virtual environment at:

```bash
/home/tom/workspace/Thesis/.venv
```

---

## Notes for Future Work
Potential future extensions that fit the current architecture:
- richer observability scoring instead of binary visible/not-visible,
- multiple targets or map points,
- more realistic camera constraints,
- trajectory replay / logging,
- export of sampled observations for thesis analysis.

If you are an AI agent modifying this project, treat this folder as a **self-contained experimental prototype** whose main mission is to support thesis research on **viewpoint visibility and observability**.
