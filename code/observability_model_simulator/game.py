import pygame
import sys
import random
import json
from pathlib import Path

import numpy as np

from observability_model import ObservabilityModels

SAVE_FILE = Path(__file__).parent / "world_save.json"

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 50, 50)
BLUE = (60, 120, 220)
GREEN = (50, 200, 50)
GOAL_RADIUS = 8
OBS_RADIUS = 3
DARK_GRAY = (40, 40, 40)
MID_GRAY = (80, 80, 80)
LIGHT_GRAY = (160, 160, 160)
TEXT_COLOR = (220, 220, 220)
MODELS = ObservabilityModels
EDIT_MODES = ["World", "Obstacle", "Observe"]
VIEW_MODES = ["Raw"] + [str(m) for m in MODELS]
MODEL_BY_NAME = {str(m): m for m in MODELS}
RESOLUTION_MODES = ["Low", "High"]
LOW_RES_BLOCK = 10

DROPDOWN_WIDTH = 200
DROPDOWN_HEIGHT = 36
MARGIN = 16


# ---------------------------------------------------------------------------
# Save / load
# ---------------------------------------------------------------------------

def save_world(world_rects: list[pygame.Rect], goal_point: tuple[int, int] | None) -> None:
    data = {
        "world_rects": [[r.x, r.y, r.width, r.height] for r in world_rects],
        "goal_point": list(goal_point) if goal_point is not None else None,
    }
    SAVE_FILE.write_text(json.dumps(data, indent=2))


def load_world() -> tuple[list[pygame.Rect], tuple[int, int] | None]:
    if not SAVE_FILE.exists():
        return [], None
    try:
        data = json.loads(SAVE_FILE.read_text())
        rects = [pygame.Rect(*r) for r in data.get("world_rects", [])]
        gp = data.get("goal_point")
        goal = tuple(gp) if gp is not None else None
        return rects, goal
    except Exception:
        return [], None


# ---------------------------------------------------------------------------
# Observation callback
# ---------------------------------------------------------------------------

def on_observe(position: tuple[int, int], visible: bool) -> None:
    for model in MODELS:
        model.add_observation(position, visible)


# ---------------------------------------------------------------------------
# Visibility ray-cast
# ---------------------------------------------------------------------------

def is_visible(
    origin: tuple[int, int],
    target: tuple[int, int],
    world_rects: list[pygame.Rect],
    obstacle_rects: list[pygame.Rect],
) -> bool:
    """Return True if the line segment from origin to target stays entirely within
    world_rects and never passes through any obstacle_rect."""
    x0, y0 = origin
    x1, y1 = target
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    for i in range(steps + 1):
        t = i / steps
        x = round(x0 + dx * t)
        y = round(y0 + dy * t)
        if not any(r.collidepoint(x, y) for r in world_rects):
            return False
        if any(r.collidepoint(x, y) for r in obstacle_rects):
            return False
    return True


# ---------------------------------------------------------------------------
# World-point sampler
# ---------------------------------------------------------------------------

def sample_world_point(
    world_rects: list[pygame.Rect],
    obstacle_rects: list[pygame.Rect],
    max_attempts: int = 10000,
) -> tuple[int, int] | None:
    """Return a uniformly random pixel that lies inside a world rect but outside all obstacle rects.
    Samples from the bounding box of all world rects to avoid over-representing small rects."""
    if not world_rects:
        return None
    left   = min(r.left   for r in world_rects)
    top    = min(r.top    for r in world_rects)
    right  = max(r.right  for r in world_rects)
    bottom = max(r.bottom for r in world_rects)
    for _ in range(max_attempts):
        x = random.randint(left, right - 1)
        y = random.randint(top, bottom - 1)
        if not any(r.collidepoint(x, y) for r in world_rects):
            continue
        if any(r.collidepoint(x, y) for r in obstacle_rects):
            continue
        return (x, y)
    return None


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def value_to_color_array(values: np.ndarray) -> np.ndarray:
    """Map a float array in [0,1] → RGB: 0→red, 0.5→yellow, 1→green."""
    v = np.clip(values, 0.0, 1.0)
    r = np.where(v <= 0.5, 255, ((1.0 - v) * 2.0 * 255).astype(np.uint8))
    g = np.where(v >= 0.5, 255, (v * 2.0 * 255).astype(np.uint8))
    b = np.zeros_like(r, dtype=np.uint8)
    return np.stack([r, g, b], axis=-1).astype(np.uint8)


def build_model_surface(
    world_rects: list[pygame.Rect],
    model,
    block_size: int = LOW_RES_BLOCK,
) -> pygame.Surface:
    """Render world rects through model.query() and return a full-window surface.

    block_size=1  → one query per pixel (high resolution).
    block_size=N  → one query per N×N block, entire block painted that color (low resolution).
    """
    surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    surf.fill(BLACK)
    for rect in world_rects:
        if rect.width == 0 or rect.height == 0:
            continue
        if block_size == 1:
            xs = np.arange(rect.left, rect.right)
            ys = np.arange(rect.top, rect.bottom)
            xx, yy = np.meshgrid(xs, ys)              # (h, w)
            coords = np.stack([xx.ravel(), yy.ravel()], axis=1)
            values = np.array([model.query((int(c[0]), int(c[1]))) for c in coords],
                              dtype=np.float32)
            colors = value_to_color_array(values.reshape(rect.height, rect.width))
            rect_surf = pygame.Surface((rect.width, rect.height))
            pygame.surfarray.blit_array(rect_surf, colors.transpose(1, 0, 2))
            surf.blit(rect_surf, (rect.left, rect.top))
        else:
            block_xs = np.arange(rect.left, rect.right, block_size)
            block_ys = np.arange(rect.top, rect.bottom, block_size)
            bxx, byy = np.meshgrid(block_xs, block_ys)    # (rows, cols)
            centers_x = np.clip(bxx + block_size // 2, rect.left, rect.right - 1)
            centers_y = np.clip(byy + block_size // 2, rect.top, rect.bottom - 1)
            coords = np.stack([centers_x.ravel(), centers_y.ravel()], axis=1)
            values = np.array([model.query((int(c[0]), int(c[1]))) for c in coords],
                              dtype=np.float32)
            colors = value_to_color_array(values)          # (n, 3)
            for i, (bx, by) in enumerate(zip(bxx.ravel(), byy.ravel())):
                bw = min(block_size, rect.right - int(bx))
                bh = min(block_size, rect.bottom - int(by))
                pygame.draw.rect(surf, tuple(colors[i]), pygame.Rect(int(bx), int(by), bw, bh))
    return surf


# ---------------------------------------------------------------------------
# UI widgets
# ---------------------------------------------------------------------------

class Button:
    def __init__(self, x, y, width, height, label, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.font = font

    def handle_event(self, event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GRAY, self.rect)
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, 1)
        text = self.font.render(self.label, True, TEXT_COLOR)
        surface.blit(
            text,
            (
                self.rect.x + (self.rect.width - text.get_width()) // 2,
                self.rect.y + (self.rect.height - text.get_height()) // 2,
            ),
        )


def normalize_rect(start, end):
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    return pygame.Rect(x, y, w, h)


class Dropdown:
    def __init__(self, x, y, width, height, label, options, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.options = options
        self.font = font
        self.selected = options[0]
        self.open = False

    def option_rect(self, index):
        return pygame.Rect(
            self.rect.x,
            self.rect.y - (index + 1) * self.rect.height,
            self.rect.width,
            self.rect.height,
        )

    def handle_event(self, event) -> bool:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        if self.rect.collidepoint(event.pos):
            self.open = not self.open
            return True
        if self.open:
            for i, option in enumerate(self.options):
                if self.option_rect(i).collidepoint(event.pos):
                    self.selected = option
                    self.open = False
                    return True
            self.open = False
        return False

    def draw(self, surface):
        lbl = self.font.render(self.label, True, TEXT_COLOR)
        surface.blit(lbl, (self.rect.x, self.rect.y - lbl.get_height() - 6))

        pygame.draw.rect(surface, DARK_GRAY, self.rect)
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, 1)
        text = self.font.render(self.selected, True, TEXT_COLOR)
        surface.blit(text, (self.rect.x + 8, self.rect.y + (self.rect.height - text.get_height()) // 2))
        arrow = self.font.render("^" if self.open else "v", True, TEXT_COLOR)
        surface.blit(arrow, (self.rect.right - arrow.get_width() - 8,
                              self.rect.y + (self.rect.height - arrow.get_height()) // 2))

        if self.open:
            for i, option in enumerate(self.options):
                r = self.option_rect(i)
                bg = MID_GRAY if option == self.selected else DARK_GRAY
                pygame.draw.rect(surface, bg, r)
                pygame.draw.rect(surface, LIGHT_GRAY, r, 1)
                opt = self.font.render(option, True, TEXT_COLOR)
                surface.blit(opt, (r.x + 8, r.y + (r.height - opt.get_height()) // 2))


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Observability Model Simulator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 18)

    edit_dropdown = Dropdown(
        MARGIN,
        WINDOW_HEIGHT - MARGIN - DROPDOWN_HEIGHT,
        DROPDOWN_WIDTH,
        DROPDOWN_HEIGHT,
        "Edit Mode",
        EDIT_MODES,
        font,
    )

    observe_button = Button(
        MARGIN + DROPDOWN_WIDTH + 16,
        WINDOW_HEIGHT - MARGIN - DROPDOWN_HEIGHT,
        120,
        DROPDOWN_HEIGHT,
        "Observe",
        font,
    )

    view_dropdown = Dropdown(
        MARGIN + DROPDOWN_WIDTH + 16 + 120 + 16,
        WINDOW_HEIGHT - MARGIN - DROPDOWN_HEIGHT,
        DROPDOWN_WIDTH,
        DROPDOWN_HEIGHT,
        "View",
        VIEW_MODES,
        font,
    )

    res_dropdown = Dropdown(
        MARGIN + DROPDOWN_WIDTH + 16 + 120 + 16 + DROPDOWN_WIDTH + 16,
        WINDOW_HEIGHT - MARGIN - DROPDOWN_HEIGHT,
        120,
        DROPDOWN_HEIGHT,
        "Resolution",
        RESOLUTION_MODES,
        font,
    )

    _btn_x = MARGIN + DROPDOWN_WIDTH + 16 + 120 + 16 + DROPDOWN_WIDTH + 16 + 120 + 16

    save_button = Button(
        _btn_x,
        WINDOW_HEIGHT - MARGIN - DROPDOWN_HEIGHT,
        90,
        DROPDOWN_HEIGHT,
        "Save",
        font,
    )

    clear_button = Button(
        _btn_x + 90 + 8,
        WINDOW_HEIGHT - MARGIN - DROPDOWN_HEIGHT,
        90,
        DROPDOWN_HEIGHT,
        "Clear",
        font,
    )

    world_rects, goal_point = load_world()
    if goal_point is not None:
        for model in MODELS:
            model.set_target(goal_point)
    obstacle_rects: list[pygame.Rect] = []
    observations: list[tuple[tuple[int, int], bool]] = []

    # Model-view cache
    model_surface: pygame.Surface | None = None
    view_dirty = True
    last_view_mode = view_dropdown.selected
    last_res_mode = res_dropdown.selected
    world_version = 0          # incremented on any world_rects change
    obs_version = 0            # incremented on each observation (model state may change)
    cached_world_version = -1
    cached_obs_version = -1

    dragging = False
    drag_start = None
    observe_dragging = False
    last_obs_pos: tuple[int, int] | None = None
    OBS_DRAG_STEP = 50  # pixels between trail observations

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if edit_dropdown.handle_event(event):
                continue

            if view_dropdown.handle_event(event):
                view_dirty = True
                continue

            if res_dropdown.handle_event(event):
                view_dirty = True
                continue

            if save_button.handle_event(event):
                save_world(world_rects, goal_point)
                continue

            if clear_button.handle_event(event):
                world_rects.clear()
                goal_point = None
                world_version += 1
                view_dirty = True
                continue

            if observe_button.handle_event(event):
                point = sample_world_point(world_rects, obstacle_rects)
                if point is not None:
                    vis = goal_point is not None and is_visible(
                        point, goal_point, world_rects, obstacle_rects
                    )
                    observations.append((point, vis))
                    on_observe(point, vis)
                    obs_version += 1
                    view_dirty = True
                continue

            mode = edit_dropdown.selected

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if mode == "Observe":
                        observe_dragging = True
                        pos = event.pos
                        in_world = any(r.collidepoint(pos) for r in world_rects)
                        in_obstacle = any(r.collidepoint(pos) for r in obstacle_rects)
                        if in_world and not in_obstacle:
                            vis = goal_point is not None and is_visible(
                                pos, goal_point, world_rects, obstacle_rects
                            )
                            observations.append((pos, vis))
                            on_observe(pos, vis)
                            obs_version += 1
                            view_dirty = True
                            last_obs_pos = pos
                    else:
                        dragging = True
                        drag_start = event.pos

                elif event.button == 3:
                    pos = event.pos
                    deleted = False
                    for i in range(len(obstacle_rects) - 1, -1, -1):
                        if obstacle_rects[i].collidepoint(pos):
                            obstacle_rects.pop(i)
                            deleted = True
                            break
                    if not deleted:
                        goal_point = pos
                        for model in MODELS:
                            model.set_target(goal_point)

            elif event.type == pygame.MOUSEMOTION:
                if observe_dragging and last_obs_pos is not None:
                    pos = event.pos
                    dx = pos[0] - last_obs_pos[0]
                    dy = pos[1] - last_obs_pos[1]
                    if dx * dx + dy * dy >= OBS_DRAG_STEP * OBS_DRAG_STEP:
                        in_world = any(r.collidepoint(pos) for r in world_rects)
                        in_obstacle = any(r.collidepoint(pos) for r in obstacle_rects)
                        if in_world and not in_obstacle:
                            vis = goal_point is not None and is_visible(
                                pos, goal_point, world_rects, obstacle_rects
                            )
                            observations.append((pos, vis))
                            on_observe(pos, vis)
                            obs_version += 1
                            view_dirty = True
                        last_obs_pos = pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    observe_dragging = False
                if event.button == 1 and dragging:
                    dragging = False
                    rect = normalize_rect(drag_start, event.pos)
                    if rect.width > 0 and rect.height > 0:
                        if mode == "World":
                            world_rects.append(rect)
                            world_version += 1
                            view_dirty = True
                        else:
                            obstacle_rects.append(rect)
                    drag_start = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    if mode == "World" and world_rects:
                        world_rects.pop()
                        world_version += 1
                        view_dirty = True

        # --- Rebuild model surface if needed ---
        view_mode = view_dropdown.selected
        if view_mode != "Raw":
            res_mode = res_dropdown.selected
            if (view_dirty
                    or view_mode != last_view_mode
                    or res_mode != last_res_mode
                    or world_version != cached_world_version
                    or obs_version != cached_obs_version):
                block_size = 1 if res_mode == "High" else LOW_RES_BLOCK
                model_surface = build_model_surface(world_rects, MODEL_BY_NAME[view_mode], block_size)
                cached_world_version = world_version
                cached_obs_version = obs_version
                view_dirty = False
        last_view_mode = view_mode
        last_res_mode = res_dropdown.selected

        # --- Render ---
        screen.fill(BLACK)

        if view_mode == "Raw":
            for r in world_rects:
                pygame.draw.rect(screen, WHITE, r)
        else:
            if model_surface is not None:
                screen.blit(model_surface, (0, 0))

        for r in obstacle_rects:
            pygame.draw.rect(screen, RED, r)

        # Drag preview
        if dragging and drag_start:
            preview = normalize_rect(drag_start, pygame.mouse.get_pos())
            if preview.width > 0 and preview.height > 0:
                color = WHITE if edit_dropdown.selected == "World" else RED
                pygame.draw.rect(screen, color, preview)

        for pos, vis in observations:
            pygame.draw.circle(screen, GREEN if vis else RED, pos, OBS_RADIUS)

        if goal_point is not None:
            pygame.draw.circle(screen, BLUE, goal_point, GOAL_RADIUS)

        edit_dropdown.draw(screen)
        observe_button.draw(screen)
        view_dropdown.draw(screen)
        res_dropdown.draw(screen)
        save_button.draw(screen)
        clear_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
