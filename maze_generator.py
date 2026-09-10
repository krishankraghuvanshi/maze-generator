import random
import os
import time
import sys
import argparse

WIDTH = 65 
HEIGHT = 33
assert WIDTH % 2 == 1 and WIDTH >= 3
assert HEIGHT % 2 == 1 and HEIGHT >= 3
SEED = 1


EMPTY = ' '
MARK = '@'
WALL = chr(9608) 
NORTH, SOUTH, EAST, WEST = 'n', 's', 'e', 'w'


DIM_PRESETS = [
    (39, 19, "Small"),
    (65, 33, "Medium"),
    (89, 45, "Large"),
    (115, 57, "Extra Large")
]


def maze_step_generator(width=WIDTH, height=HEIGHT, seed=None):
    """
    Iterative generator for maze generation (Depth-First Search with backtracking).
    Yields (maze_dict, mark_x, mark_y, is_finished, step_count).
    """
    if seed is not None:
        random.seed(seed)

    maze = {(x, y): WALL for x in range(width) for y in range(height)}
    
    stack = [(1, 1)]
    has_visited = {(1, 1)}
    maze[(1, 1)] = EMPTY
    step_count = 0

    yield maze, 1, 1, False, step_count

    while stack:
        x, y = stack[-1]

        unvisited_neighbors = []
        if y > 1 and (x, y - 2) not in has_visited:
            unvisited_neighbors.append((NORTH, x, y - 2, x, y - 1))
        if y < height - 2 and (x, y + 2) not in has_visited:
            unvisited_neighbors.append((SOUTH, x, y + 2, x, y + 1))
        if x > 1 and (x - 2, y) not in has_visited:
            unvisited_neighbors.append((WEST, x - 2, y, x - 1, y))
        if x < width - 2 and (x + 2, y) not in has_visited:
            unvisited_neighbors.append((EAST, x + 2, y, x + 1, y))

        if not unvisited_neighbors:
            stack.pop()
            step_count += 1
            if stack:
                prev_x, prev_y = stack[-1]
                yield maze, prev_x, prev_y, False, step_count
        else:
            direction, next_x, next_y, wall_x, wall_y = random.choice(unvisited_neighbors)
            maze[(wall_x, wall_y)] = EMPTY
            maze[(next_x, next_y)] = EMPTY
            has_visited.add((next_x, next_y))
            stack.append((next_x, next_y))
            step_count += 1
            yield maze, next_x, next_y, False, step_count

    yield maze, None, None, True, step_count


def run_cli_mode(width=WIDTH, height=HEIGHT, seed=SEED):
    """Classic CLI execution mode in the terminal console."""
    print(f"Starting Maze Generator in CLI mode ({width}x{height})...")
    gen = maze_step_generator(width, height, seed)
    try:
        for maze, mark_x, mark_y, is_finished, _ in gen:
            os.system('cls' if os.name == 'nt' else 'clear')
            for y in range(height):
                row = []
                for x in range(width):
                    if mark_x == x and mark_y == y:
                        row.append(MARK)
                    else:
                        row.append(maze[(x, y)])
                print(''.join(row))
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("\nExited CLI simulation.")
        return
    print("\nMaze generation complete!")


def run_gui_terminal_mode(start_w=WIDTH, start_h=HEIGHT):
    """Interactive GUI Window styled like a retro terminal with dynamic cell scaling."""
    try:
        import pygame
    except ImportError:
        print("Pygame library missing. Running in standard CLI mode...")
        run_cli_mode(start_w, start_h)
        return

    pygame.init()
    pygame.font.init()

    # Color Themes
    THEMES = [
        {
            "name": "Monochrome White",
            "bg": (13, 17, 23),
            "header_bg": (22, 27, 34),
            "wall": (255, 255, 255),
            "empty": (45, 52, 64),
            "mark": (255, 215, 0),
            "text": (240, 246, 252),
            "accent": (255, 255, 255)
        },
        {
            "name": "Matrix Cyber",
            "bg": (10, 16, 13),
            "header_bg": (18, 28, 23),
            "wall": (0, 255, 102),
            "empty": (20, 45, 30),
            "mark": (255, 230, 0),
            "text": (140, 255, 180),
            "accent": (0, 255, 170)
        },
        {
            "name": "Cyberpunk Neon",
            "bg": (15, 18, 30),
            "header_bg": (28, 32, 54),
            "wall": (0, 229, 255),
            "empty": (30, 36, 60),
            "mark": (255, 0, 110),
            "text": (200, 220, 255),
            "accent": (255, 0, 110)
        },
        {
            "name": "Classic Amber",
            "bg": (18, 10, 2),
            "header_bg": (32, 18, 5),
            "wall": (255, 176, 0),
            "empty": (50, 30, 5),
            "mark": (255, 255, 255),
            "text": (255, 200, 100),
            "accent": (255, 176, 0)
        },
        {
            "name": "Synthwave Glow",
            "bg": (20, 10, 25),
            "header_bg": (35, 18, 45),
            "wall": (180, 75, 255),
            "empty": (45, 20, 60),
            "mark": (0, 255, 200),
            "text": (230, 180, 255),
            "accent": (180, 75, 255)
        }
    ]
    current_theme_idx = 0
    current_dim_idx = 1 # Default to Medium (65x33)

    # Set current width/height
    cur_width, cur_height = start_w, start_h

    HEADER_HEIGHT = 42
    FOOTER_HEIGHT = 70

    # Calculate optimal cell size and window dimensions dynamically
    def calculate_layout(w, h):
        # Target screen fit bounds
        max_canvas_w = 1200
        max_canvas_h = 650

        cell_w = max(8, min(22, max_canvas_w // w))
        cell_h = max(10, min(26, max_canvas_h // h))

        grid_pixel_w = w * cell_w
        grid_pixel_h = h * cell_h

        win_w = max(grid_pixel_w + 60, 960)
        win_h = HEADER_HEIGHT + grid_pixel_h + FOOTER_HEIGHT + 30

        font_size = max(9, min(18, cell_h - 4))
        mono_font = pygame.font.SysFont(["Menlo", "Monaco", "Courier New", "Consolas", "monospace"], font_size, bold=True)

        return cell_w, cell_h, grid_pixel_w, grid_pixel_h, win_w, win_h, mono_font

    cell_w, cell_h, grid_pixel_w, grid_pixel_h, window_w, window_h, font_mono = calculate_layout(cur_width, cur_height)

    screen = pygame.display.set_mode((window_w, window_h))
    pygame.display.set_caption(f"Terminal - Maze Simulation ({cur_width}x{cur_height})")

    font_ui = pygame.font.SysFont(["SF Pro Text", "Helvetica", "Arial", "sans-serif"], 14, bold=True)
    font_small = pygame.font.SysFont(["Menlo", "Monaco", "Courier New", "monospace"], 13)

    # Simulation state
    seed_val = SEED
    step_gen = maze_step_generator(cur_width, cur_height, seed_val)
    current_state = next(step_gen)
    
    paused = False
    finished = False
    fps = 60
    clock = pygame.time.Clock()

    running = True

    while running:
        theme = THEMES[current_theme_idx]

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    seed_val += 1
                    step_gen = maze_step_generator(cur_width, cur_height, seed_val)
                    current_state = next(step_gen)
                    finished = False
                    paused = False
                elif event.key == pygame.K_c:
                    current_theme_idx = (current_theme_idx + 1) % len(THEMES)
                elif event.key == pygame.K_d:
                    # Toggle dimension preset
                    current_dim_idx = (current_dim_idx + 1) % len(DIM_PRESETS)
                    cur_width, cur_height, label = DIM_PRESETS[current_dim_idx]
                    cell_w, cell_h, grid_pixel_w, grid_pixel_h, window_w, window_h, font_mono = calculate_layout(cur_width, cur_height)
                    screen = pygame.display.set_mode((window_w, window_h))
                    pygame.display.set_caption(f"Terminal - Maze Simulation ({cur_width}x{cur_height})")
                    step_gen = maze_step_generator(cur_width, cur_height, seed_val)
                    current_state = next(step_gen)
                    finished = False
                    paused = False
                elif event.key == pygame.K_UP:
                    fps = min(fps + 10, 240)
                elif event.key == pygame.K_DOWN:
                    fps = max(fps - 10, 5)

        # Update step if active
        if not paused and not finished:
            try:
                current_state = next(step_gen)
                maze, mark_x, mark_y, finished, step_count = current_state
            except StopIteration:
                finished = True

        maze, mark_x, mark_y, finished, step_count = current_state

        # Rendering
        screen.fill(theme["bg"])

        # 1. Header (Terminal Bar)
        pygame.draw.rect(screen, theme["header_bg"], (0, 0, window_w, HEADER_HEIGHT))
        pygame.draw.line(screen, theme["wall"], (0, HEADER_HEIGHT), (window_w, HEADER_HEIGHT), 1)

        # macOS Window Control Buttons
        pygame.draw.circle(screen, (255, 95, 86), (20, 21), 6)
        pygame.draw.circle(screen, (255, 189, 46), (38, 21), 6)
        pygame.draw.circle(screen, (39, 201, 63), (56, 21), 6)

        # Header Title
        title_text = f"zsh - maze_generator.py [{cur_width}x{cur_height}] - Theme: {theme['name']}"
        title_surf = font_ui.render(title_text, True, theme["text"])
        screen.blit(title_surf, (window_w // 2 - title_surf.get_width() // 2, 12))

        # 2. Render Maze Grid
        grid_start_x = (window_w - grid_pixel_w) // 2
        grid_start_y = HEADER_HEIGHT + 15

        # Terminal border box
        pygame.draw.rect(
            screen,
            theme["header_bg"],
            (grid_start_x - 8, grid_start_y - 8, grid_pixel_w + 16, grid_pixel_h + 16),
            border_radius=6
        )
        pygame.draw.rect(
            screen,
            theme["wall"],
            (grid_start_x - 8, grid_start_y - 8, grid_pixel_w + 16, grid_pixel_h + 16),
            width=1,
            border_radius=6
        )

        for y in range(cur_height):
            for x in range(cur_width):
                pos_x = grid_start_x + x * cell_w
                pos_y = grid_start_y + y * cell_h

                if x == mark_x and y == mark_y:
                    cell_bg = pygame.Surface((cell_w, cell_h))
                    cell_bg.set_alpha(90)
                    cell_bg.fill(theme["mark"])
                    screen.blit(cell_bg, (pos_x, pos_y))

                    txt_surf = font_mono.render(MARK, True, theme["mark"])
                    screen.blit(txt_surf, (pos_x + (cell_w - txt_surf.get_width()) // 2, pos_y + (cell_h - txt_surf.get_height()) // 2))
                else:
                    ch = maze.get((x, y), WALL)
                    if ch == WALL:
                        txt_surf = font_mono.render(WALL, True, theme["wall"])
                    else:
                        txt_surf = font_mono.render("·", True, theme["empty"])
                    screen.blit(txt_surf, (pos_x + (cell_w - txt_surf.get_width()) // 2, pos_y + (cell_h - txt_surf.get_height()) // 2))

        # 3. Render Status & Footer Info Bar
        footer_top = window_h - FOOTER_HEIGHT
        pygame.draw.line(screen, theme["header_bg"], (0, footer_top), (window_w, footer_top), 1)

        # Status badge
        if finished:
            status_str = "[ FINISHED ]"
            status_color = (0, 255, 150)
        elif paused:
            status_str = "[ PAUSED ]"
            status_color = (255, 200, 50)
        else:
            status_str = "[ GENERATING... ]"
            status_color = theme["accent"]

        status_surf = font_ui.render(status_str, True, status_color)
        screen.blit(status_surf, (20, footer_top + 12))

        pos_str = f"Dimensions: {cur_width}x{cur_height} | Pos: ({mark_x if mark_x is not None else '-'}, {mark_y if mark_y is not None else '-'}) | Steps: {step_count} | Seed: {seed_val}"
        info_surf = font_small.render(pos_str, True, theme["text"])
        screen.blit(info_surf, (20, footer_top + 38))

        # Key shortcuts
        keys_str = f"[SPACE] Pause | [R] Restart | [D] Size ({cur_width}x{cur_height}) | [C] Theme | [↑/↓] Speed: {fps} FPS"
        keys_surf = font_small.render(keys_str, True, theme["accent"])
        screen.blit(keys_surf, (window_w - keys_surf.get_width() - 20, footer_top + 24))

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Terminal Maze Generator Simulation")
    parser.add_argument("--cli", action="store_true", help="Run in standard CLI terminal mode")
    parser.add_argument("--width", type=int, default=WIDTH, help="Maze width (odd number >= 3)")
    parser.add_argument("--height", type=int, default=HEIGHT, help="Maze height (odd number >= 3)")
    args = parser.parse_args()

    # Ensure odd dimensions
    w = args.width if args.width % 2 == 1 else args.width + 1
    h = args.height if args.height % 2 == 1 else args.height + 1

    if args.cli:
        run_cli_mode(w, h)
    else:
        run_gui_terminal_mode(w, h)