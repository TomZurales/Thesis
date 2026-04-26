import pygame
import sys
import os
from collections import deque
import numpy as np

from vbee_2d.vbee import VBEE
from vbee_2d.observability_models.discrete_boundary import DiscreteBoundary

ASPECT = 16 / 9
BASE_W = 1280
BASE_H = 720
TOOLBAR_H = 44

COLS = 80
ROWS = 45

EMPTY = 0
WALL  = 1
GOAL  = 2

MODE_EDIT = "edit"
MODE_RUN  = "run"

TOOL_WALL = "Wall"
TOOL_FILL = "Fill"
TOOL_GOAL = "Goal"
TOOLS = [TOOL_WALL, TOOL_FILL, TOOL_GOAL]

BTN_W        = 90
BTN_H        = 30
BTN_PAD      = 8
DROPDOWN_W   = 210
RENDER_BTN_W = 185

ALGO_OPTIONS = [
    "KNN (k=1)",
    "KNN (k=5)",
    "Discrete Boundary (n=4)",
    "Discrete Boundary (n=20)",
]

SAVE_FILE = "world.npy"

COLOR_VISIBLE  = (30, 180, 30)
COLOR_OCCLUDED = (210, 30, 30)
COLOR_GOAL     = (30, 80, 210)
GOAL_RADIUS   = 5
OBS_RADIUS   = 2

vbee = None

# ---------------------------------------------------------------------------
# Run-mode entry point — implement this function
# ---------------------------------------------------------------------------
def on_next(_observations: list[tuple[float, float, bool]]) -> None:
    vbee.step(_observations)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def compute_size(w, h):
    if w / h > ASPECT:
        w = int(h * ASPECT)
    else:
        h = int(w / ASPECT)
    return w, h


def get_cell(mx, my, win_w, win_h):
    if my < TOOLBAR_H:
        return None, None
    cell_w = win_w / COLS
    cell_h = (win_h - TOOLBAR_H) / ROWS
    col = int(mx / cell_w)
    row = int((my - TOOLBAR_H) / cell_h)
    if 0 <= col < COLS and 0 <= row < ROWS:
        return row, col
    return None, None


def flood_fill(grid, start_r, start_c):
    if grid[start_r, start_c] != EMPTY:
        return
    queue = deque([(start_r, start_c)])
    seen = {(start_r, start_c)}
    while queue:
        r, c = queue.popleft()
        grid[r, c] = WALL
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and (nr, nc) not in seen and grid[nr, nc] == EMPTY:
                seen.add((nr, nc))
                queue.append((nr, nc))


def has_goal(grid):
    return bool(np.any(grid == GOAL))


def find_goal(grid):
    positions = np.argwhere(grid == GOAL)
    return tuple(positions[0]) if len(positions) else None  # (row, col)


def ray_traversed_cells(sx, sy, ex, ey):
    """Return the set of (row, col) cells that the segment crosses.

    All coordinates are in fractional grid-space where x=col, y=row.
    Uses DDA grid traversal.
    """
    c0, r0 = int(sx), int(sy)
    c1, r1 = int(ex), int(ey)

    dx = ex - sx
    dy = ey - sy

    step_c = 1 if dx > 0 else -1
    step_r = 1 if dy > 0 else -1

    if dx != 0:
        t_max_c = ((c0 + (1 if step_c > 0 else 0)) - sx) / dx
        t_delta_c = abs(1.0 / dx)
    else:
        t_max_c = float('inf')
        t_delta_c = float('inf')

    if dy != 0:
        t_max_r = ((r0 + (1 if step_r > 0 else 0)) - sy) / dy
        t_delta_r = abs(1.0 / dy)
    else:
        t_max_r = float('inf')
        t_delta_r = float('inf')

    c, r = c0, r0
    cells = {(r, c)}

    for _ in range(abs(c1 - c0) + abs(r1 - r0) + 2):
        if c == c1 and r == r1:
            break
        if t_max_c <= t_max_r:
            c += step_c
            t_max_c += t_delta_c
        else:
            r += step_r
            t_max_r += t_delta_r
        if 0 <= r < ROWS and 0 <= c < COLS:
            cells.add((r, c))

    return cells


def ray_clear(px, py, goal_row, goal_col, grid, cell_w, cell_h):
    """Return True if the ray from pixel (px, py) to the goal cell centre is unobstructed."""
    sx = px / cell_w
    sy = (py - TOOLBAR_H) / cell_h
    ex = goal_col + 0.5
    ey = goal_row + 0.5

    for (r, c) in ray_traversed_cells(sx, sy, ex, ey):
        if grid[r, c] == WALL:
            return False
    return True


def heatmap_color(value: float) -> tuple[int, int, int]:
    """Map a [0, 1] value to a red→yellow→green color."""
    v = max(0.0, min(1.0, value))
    r = round(255 * min(1.0, (1.0 - v) * 2))
    g = round(255 * min(1.0, v * 2))
    return (r, g, 0)


def compute_heatmap(grid, win_w, win_h, model: str) -> pygame.Surface:
    """Render a per-pixel heatmap of vbee.query for every non-wall pixel.
    Returns a Surface sized (win_w, grid_h) — blit it at (0, TOOLBAR_H)."""
    grid_h = win_h - TOOLBAR_H
    cell_w = win_w / COLS
    cell_h = grid_h / ROWS

    # Pixel→cell mapping derived from the same round() formula used by wall
    # rects, so boundaries are guaranteed to be consistent (no white gaps).
    row_of = np.empty(grid_h, dtype=np.int32)
    for r in range(ROWS):
        row_of[round(r * cell_h):round((r + 1) * cell_h)] = r

    col_of = np.empty(win_w, dtype=np.int32)
    for c in range(COLS):
        col_of[round(c * cell_w):round((c + 1) * cell_w)] = c

    # surfarray uses (width, height) column-major indexing
    pixels = np.full((win_w, grid_h, 3), 255, dtype=np.uint8)

    goal = find_goal(grid)
    gx_screen = (goal[1] + 0.5) * cell_w if goal else 0.0
    gy_screen = TOOLBAR_H + (goal[0] + 0.5) * cell_h if goal else 0.0

    for py in range(grid_h):
        r = row_of[py]
        rel_y = TOOLBAR_H + py - gy_screen
        for px in range(win_w):
            if grid[r, col_of[px]] != WALL:
                pixels[px, py] = heatmap_color(vbee.query((px - gx_screen, rel_y)))

    return pygame.surfarray.make_surface(pixels)


def try_place_observation(mx, my, grid, run_points, win_w, win_h):
    """Place an observation at (mx, my) if the cell is not a wall. Returns True if placed."""
    row, col = get_cell(mx, my, win_w, win_h)
    if row is None or grid[row, col] == WALL:
        return False
    goal = find_goal(grid)
    cell_w = win_w / COLS
    cell_h = (win_h - TOOLBAR_H) / ROWS
    if goal and ray_clear(mx, my, goal[0], goal[1], grid, cell_w, cell_h):
        color = COLOR_VISIBLE
    else:
        color = COLOR_OCCLUDED
    run_points.append((mx, my, color))
    return True


# ---------------------------------------------------------------------------
# Toolbar drawing
# ---------------------------------------------------------------------------
def edit_toolbar_rects():
    rects = {}
    x = BTN_PAD
    y = (TOOLBAR_H - BTN_H) // 2
    for tool in TOOLS:
        rects[tool] = pygame.Rect(x, y, BTN_W, BTN_H)
        x += BTN_W + BTN_PAD
    x += BTN_PAD
    for label in ("Save", "Clear"):
        rects[label] = pygame.Rect(x, y, BTN_W, BTN_H)
        x += BTN_W + BTN_PAD
    x += BTN_PAD
    rects["Done"] = pygame.Rect(x, y, BTN_W, BTN_H)
    return rects


def run_toolbar_rects():
    rects = {}
    x = BTN_PAD
    y = (TOOLBAR_H - BTN_H) // 2
    for label in ("Edit", "Next"):
        rects[label] = pygame.Rect(x, y, BTN_W, BTN_H)
        x += BTN_W + BTN_PAD
    x += BTN_PAD  # extra gap before dropdown
    rects["Dropdown"] = pygame.Rect(x, y, DROPDOWN_W, BTN_H)
    x += DROPDOWN_W + BTN_PAD
    rects["Render Observability"] = pygame.Rect(x, y, RENDER_BTN_W, BTN_H)
    return rects


def dropdown_option_rects(dropdown_rect):
    return [
        pygame.Rect(dropdown_rect.x, dropdown_rect.bottom + i * BTN_H,
                    dropdown_rect.width, BTN_H)
        for i in range(len(ALGO_OPTIONS))
    ]


def draw_button(screen, rect, label, font, active=True, selected=False):
    if not active:
        bg, border, fg = (60, 60, 60), (80, 80, 80), (120, 120, 120)
    elif selected:
        bg, border, fg = (70, 130, 210), (120, 170, 240), (240, 240, 240)
    else:
        bg, border, fg = (90, 90, 90), (130, 130, 130), (240, 240, 240)
    pygame.draw.rect(screen, bg, rect, border_radius=4)
    pygame.draw.rect(screen, border, rect, width=1, border_radius=4)
    text = font.render(label, True, fg)
    screen.blit(text, text.get_rect(center=rect.center))


def draw_edit_toolbar(screen, win_w, active_tool, goal_placed, font):
    pygame.draw.rect(screen, (45, 45, 45), (0, 0, win_w, TOOLBAR_H))
    for label, rect in edit_toolbar_rects().items():
        if label == "Done":
            draw_button(screen, rect, label, font, active=goal_placed)
        elif label in TOOLS:
            draw_button(screen, rect, label, font, selected=(label == active_tool))
        else:
            draw_button(screen, rect, label, font)


def draw_run_toolbar(screen, win_w, font, algo_index, dropdown_open):
    pygame.draw.rect(screen, (45, 45, 45), (0, 0, win_w, TOOLBAR_H))
    rects = run_toolbar_rects()
    for label, rect in rects.items():
        if label == "Dropdown":
            draw_button(screen, rect, ALGO_OPTIONS[algo_index] + "  ▼", font)
        else:
            draw_button(screen, rect, label, font)

    if dropdown_open:
        for i, orect in enumerate(dropdown_option_rects(rects["Dropdown"])):
            pygame.draw.rect(screen, (30, 30, 30), orect)
            pygame.draw.rect(screen, (100, 100, 100), orect, width=1)
            draw_button(screen, orect, ALGO_OPTIONS[i], font, selected=(i == algo_index))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    global vbee
    pygame.init()
    font = pygame.font.SysFont(None, 26)

    win_w, win_h = BASE_W, BASE_H
    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption("2D VBEE Simulator")

    if os.path.exists(SAVE_FILE):
        grid = np.load(SAVE_FILE)
    else:
        grid = np.zeros((ROWS, COLS), dtype=np.int8)

    clock = pygame.time.Clock()
    mode = MODE_EDIT
    dragging = False
    drag_value = WALL
    active_tool = TOOL_WALL
    run_points = []      # list of (px, py, color)
    last_obs_pos = None  # pixel position of last placed observation
    algo_index    = 0
    dropdown_open = False
    obs_surface   = None  # heatmap Surface, or None when not rendered

    while True:
        goal_placed = has_goal(grid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                win_w, win_h = compute_size(event.w, event.h)
                screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if mode == MODE_EDIT:
                    if my < TOOLBAR_H:
                        for label, rect in edit_toolbar_rects().items():
                            if rect.collidepoint(mx, my):
                                if label == "Done" and goal_placed:
                                    mode = MODE_RUN
                                    if vbee is None:
                                        vbee = VBEE(find_goal(grid), DiscreteBoundary(20))
                                    dragging = False
                                elif label in TOOLS:
                                    active_tool = label
                                    dragging = False
                                elif label == "Save":
                                    np.save(SAVE_FILE, grid)
                                elif label == "Clear":
                                    grid[:] = EMPTY
                                break
                    else:
                        row, col = get_cell(mx, my, win_w, win_h)
                        if row is not None:
                            if active_tool == TOOL_WALL:
                                drag_value = EMPTY if grid[row, col] == WALL else WALL
                                grid[row, col] = drag_value
                                dragging = True
                            elif active_tool == TOOL_FILL:
                                flood_fill(grid, row, col)
                            elif active_tool == TOOL_GOAL:
                                if grid[row, col] == EMPTY:
                                    grid[grid == GOAL] = EMPTY
                                    grid[row, col] = GOAL
                                    vbee = VBEE(find_goal(grid), DiscreteBoundary(20))

                elif mode == MODE_RUN:
                    tb_rects = run_toolbar_rects()

                    # Dropdown options sit below the toolbar — check them first
                    if dropdown_open:
                        hit = False
                        for i, orect in enumerate(dropdown_option_rects(tb_rects["Dropdown"])):
                            if orect.collidepoint(mx, my):
                                algo_index = i
                                dropdown_open = False
                                hit = True
                                break
                        if hit:
                            pass
                        elif my < TOOLBAR_H:
                            dropdown_open = False  # toolbar click elsewhere closes it
                        else:
                            dropdown_open = False  # grid click closes it

                    elif my < TOOLBAR_H:
                        for label, rect in tb_rects.items():
                            if rect.collidepoint(mx, my):
                                if label == "Edit":
                                    mode = MODE_EDIT
                                    run_points.clear()
                                elif label == "Next":
                                    goal = find_goal(grid)
                                    cell_w = win_w / COLS
                                    cell_h = (win_h - TOOLBAR_H) / ROWS
                                    gx = (goal[1] + 0.5) * cell_w
                                    gy = TOOLBAR_H + (goal[0] + 0.5) * cell_h
                                    obs = [
                                        (px - gx, py - gy, color == COLOR_VISIBLE)
                                        for px, py, color in run_points
                                    ]
                                    on_next(obs)
                                    run_points.clear()
                                    obs_surface = None
                                elif label == "Dropdown":
                                    dropdown_open = True
                                elif label == "Render Observability":
                                    obs_surface = compute_heatmap(grid, win_w, win_h, ALGO_OPTIONS[algo_index])
                                break

                    else:
                        if try_place_observation(mx, my, grid, run_points, win_w, win_h):
                            dragging = True
                            last_obs_pos = (mx, my)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False

            elif event.type == pygame.MOUSEMOTION and dragging:
                mx, my = event.pos
                if mode == MODE_EDIT and active_tool == TOOL_WALL:
                    row, col = get_cell(mx, my, win_w, win_h)
                    if row is not None:
                        grid[row, col] = drag_value
                elif mode == MODE_RUN and last_obs_pos is not None:
                    dx = mx - last_obs_pos[0]
                    dy = my - last_obs_pos[1]
                    if dx * dx + dy * dy >= 25 * 25:
                        if try_place_observation(mx, my, grid, run_points, win_w, win_h):
                            last_obs_pos = (mx, my)

        # ----------------------------------------------------------------
        # Render
        # ----------------------------------------------------------------
        screen.fill((255, 255, 255))

        grid_h = win_h - TOOLBAR_H
        cell_w = win_w / COLS
        cell_h = grid_h / ROWS

        # Heatmap goes first so walls render on top
        if mode == MODE_RUN and obs_surface is not None:
            screen.blit(obs_surface, (0, TOOLBAR_H))

        for r in range(ROWS):
            for c in range(COLS):
                val = grid[r, c]
                x0 = round(c * cell_w)
                y0 = TOOLBAR_H + round(r * cell_h)
                x1 = round((c + 1) * cell_w)
                y1 = TOOLBAR_H + round((r + 1) * cell_h)
                if val == WALL:
                    pygame.draw.rect(screen, (0, 0, 0), (x0, y0, x1 - x0, y1 - y0))
                elif val == GOAL:
                    cx = (x0 + x1) // 2
                    cy = (y0 + y1) // 2
                    radius = max(2, round(min(cell_w, cell_h) * 0.3))
                    pygame.draw.circle(screen, COLOR_GOAL, (cx, cy), radius)

        if mode == MODE_EDIT:
            grid_color = (220, 220, 220)
            for c in range(COLS + 1):
                x = round(c * cell_w)
                pygame.draw.line(screen, grid_color, (x, TOOLBAR_H), (x, win_h))
            for r in range(ROWS + 1):
                y = TOOLBAR_H + round(r * cell_h)
                pygame.draw.line(screen, grid_color, (0, y), (win_w, y))
            draw_edit_toolbar(screen, win_w, active_tool, goal_placed, font)
        else:
            for px, py, color in run_points:
                pygame.draw.circle(screen, color, (px, py), OBS_RADIUS)
            draw_run_toolbar(screen, win_w, font, algo_index, dropdown_open)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
