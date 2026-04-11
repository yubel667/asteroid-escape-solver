import pygame
import sys
import time
from board import BoardState

# Colors
BACKGROUND = (10, 12, 20)
GRID_LINE = (30, 35, 50)
TILE_BORDER = (60, 70, 90)
EMPTY = (5, 7, 12)
COSMOS_TILE = (25, 35, 60) # Dark Blue Cosmos color

COLOR_MAP = {
    0: (80, 180, 255),    # Ship (Blue)
    1: (180, 140, 100),   # Small asteroid
    2: (180, 140, 100),
    3: (180, 140, 100),
    4: (140, 100, 80),    # Big asteroid
    5: (140, 100, 80),
}

# Variable grid sizes to make 2x2 look
C_SIZE = 60
M_SIZE = 12
B_SIZE = 25
UNIT_SIZES = [B_SIZE, C_SIZE, M_SIZE, C_SIZE, C_SIZE, M_SIZE, C_SIZE, C_SIZE, M_SIZE, C_SIZE, B_SIZE]
MARGIN = 30
ANIMATION_DURATION = 0.4  # Seconds for the slide
MOVE_DELAY = 0.3       # Seconds to wait after the slide
TOTAL_STEP_TIME = ANIMATION_DURATION + MOVE_DELAY

def get_unit_pos(idx):
    pos = MARGIN
    for i in range(idx):
        pos += UNIT_SIZES[i]
    return pos, pos + UNIT_SIZES[idx] / 2

def get_tile_pixel_center(tj, ti):
    _, cj = get_unit_pos(2 + tj * 3)
    _, ci = get_unit_pos(2 + ti * 3)
    return cj, ci

def get_tile_pixel_bounds(tj, ti):
    y, _ = get_unit_pos(1 + tj * 3)
    x, _ = get_unit_pos(1 + ti * 3)
    h = UNIT_SIZES[1+tj*3] + UNIT_SIZES[2+tj*3] + UNIT_SIZES[3+tj*3]
    w = UNIT_SIZES[1+ti*3] + UNIT_SIZES[2+ti*3] + UNIT_SIZES[3+ti*3]
    return x, y, w, h

def draw_piece(screen, state, pid, pix_cj, pix_ci, scale=1.0):
    if state:
        piece = state.setup.pieces[pid]
    else:
        from board import PIECES
        piece = PIECES[pid]
    color = COLOR_MAP.get(piece.piece_id, (200, 200, 200))
    sc_c, sc_m = C_SIZE * scale, M_SIZE * scale
    if piece.is_ship:
        S_UP = 0
        body_cj = pix_cj - (sc_m/2 + sc_c/2) + S_UP
        body_width = 4 * sc_c + sc_m
        pygame.draw.rect(screen, color, (pix_ci - body_width/2 + 4*scale, body_cj - sc_c/2 + 4*scale, body_width - 8*scale, sc_c - 8*scale), 0, int(10*scale))
        base_y, tip_y = body_cj + sc_c/2, pix_cj + sc_m/2 + sc_c * 0.9 + S_UP
        pygame.draw.polygon(screen, color, [(pix_ci - 18*scale, base_y), (pix_ci + 18*scale, base_y), (pix_ci, tip_y)])
    else:
        is_big = piece.piece_id in [4, 5]
        if is_big:
            sum_dx, sum_dy = 0, 0
            for cell in piece.cells:
                dy = (sc_m/2 + sc_c/2) if cell.y == 1 else -(sc_m/2 + sc_c/2) if cell.y == -1 else (sc_m/2 + sc_c + sc_c/2) if cell.y == 2 else -(sc_m/2 + sc_c + sc_c/2) if cell.y == -2 else 0
                dx = (sc_m/2 + sc_c/2) if cell.x == 1 else -(sc_m/2 + sc_c/2) if cell.x == -1 else (sc_m/2 + sc_c + sc_c/2) if cell.x == 2 else -(sc_m/2 + sc_c + sc_c/2) if cell.x == -2 else 0
                sum_dy, sum_dx = sum_dy + dy, sum_dx + dx
            avg_cy, avg_cx = pix_cj + sum_dy / len(piece.cells), pix_ci + sum_dx / len(piece.cells)
            # average further towards center
            DRAG = 0.3
            avg_cy = pix_cj * DRAG + avg_cy * (1 - DRAG)
            avg_cx = pix_ci * DRAG + avg_cx * (1 - DRAG)
            radius = sc_c * 0.9
            pygame.draw.circle(screen, color, (int(avg_cx), int(avg_cy)), int(radius))
            pygame.draw.circle(screen, (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30)), (int(avg_cx), int(avg_cy)), int(radius), max(1, int(3*scale)))
        else:
            grid_pos = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for cell in piece.cells:
                if (cell.y, cell.x) in grid_pos:
                    off_y = (sc_m/2 + sc_c/2) if cell.y == 1 else -(sc_m/2 + sc_c/2)
                    off_x = (sc_m/2 + sc_c/2) if cell.x == 1 else -(sc_m/2 + sc_c/2)
                    radius = sc_c * 0.45
                    pygame.draw.circle(screen, color, (int(pix_ci + off_x), int(pix_cj + off_y)), int(radius))
                    pygame.draw.circle(screen, (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30)), (int(pix_ci + off_x), int(pix_cj + off_y)), int(radius), max(1, int(2*scale)))

def draw_board_chrome(screen):
    screen.fill(BACKGROUND)
    for idx in [1, 4, 7, 10]:
        pos = MARGIN + sum(UNIT_SIZES[:idx])
        pygame.draw.line(screen, TILE_BORDER, (MARGIN, pos), (MARGIN + sum(UNIT_SIZES), pos), 2)
        pygame.draw.line(screen, TILE_BORDER, (pos, MARGIN), (pos, MARGIN + sum(UNIT_SIZES)), 2)
    start_x, end_x, y_pos = MARGIN + sum(UNIT_SIZES[:4]), MARGIN + sum(UNIT_SIZES[:7]), MARGIN + sum(UNIT_SIZES[:10])
    pygame.draw.rect(screen, (0, 255, 120), (start_x, y_pos, end_x - start_x, 10), 0, 5)

def draw_board(screen, state: BoardState, move_info=None, alpha=0.0, level_id=None):
    draw_board_chrome(screen)
    moving_f, moving_t = move_info if move_info else (None, None)
    piece_draw_data, ship_rendered = [], False
    ship_pid = next((i for i, p in enumerate(state.setup.pieces) if p.is_ship), None)
    for tj in range(3):
        for ti in range(3):
            pid = state.board[tj, ti]
            if pid == 8: continue
            if pid == ship_pid: ship_rendered = True
            cj, ci = get_tile_pixel_center(tj, ti)
            bx, by, bw, bh = get_tile_pixel_bounds(tj, ti)
            if (tj, ti) == moving_f:
                target_j, target_i = moving_t
                if target_j == 3: # Exit
                    offset = sum(UNIT_SIZES[1:4])
                    target_cj, target_ci, target_by, target_bx = cj + offset, ci, by + offset, bx
                else:
                    target_cj, target_ci = get_tile_pixel_center(target_j, target_i)
                    target_bx, target_by, _, _ = get_tile_pixel_bounds(target_j, target_i)
                cur_cj, cur_ci, cur_bx, cur_by = cj + (target_cj - cj) * alpha, ci + (target_ci - ci) * alpha, bx + (target_bx - bx) * alpha, by + (target_by - by) * alpha
                if pid == ship_pid: ship_rendered = True
            else: cur_cj, cur_ci, cur_bx, cur_by = cj, ci, bx, by
            pygame.draw.rect(screen, COSMOS_TILE, (cur_bx + 2, cur_by + 2, bw - 4, bh - 4), 0, 12)
            pygame.draw.rect(screen, (max(0, COSMOS_TILE[0]-10), max(0, COSMOS_TILE[1]-10), max(0, COSMOS_TILE[2]-10)), (cur_bx + 2, cur_by + 2, bw - 4, bh - 4), 2, 12)
            piece_draw_data.append((pid, cur_cj, cur_ci))
    if not ship_rendered and ship_pid is not None:
        cj, ci = get_tile_pixel_center(2, 1)
        bx, by, bw, bh = get_tile_pixel_bounds(2, 1)
        offset = sum(UNIT_SIZES[1:4])
        cur_cj, cur_ci, cur_bx, cur_by = cj + offset, ci, bx, by + offset
        pygame.draw.rect(screen, COSMOS_TILE, (cur_bx + 2, cur_by + 2, bw - 4, bh - 4), 0, 12)
        pygame.draw.rect(screen, (max(0, COSMOS_TILE[0]-10), max(0, COSMOS_TILE[1]-10), max(0, COSMOS_TILE[2]-10)), (cur_bx + 2, cur_by + 2, bw - 4, bh - 4), 2, 12)
        piece_draw_data.append((ship_pid, cur_cj, cur_ci))
    for pid, cur_cj, cur_ci in piece_draw_data: draw_piece(screen, state, pid, cur_cj, cur_ci)
    if level_id:
        img = pygame.font.SysFont(None, 28, bold=True).render(f"LEVEL: {level_id}", True, (180, 190, 210))
        screen.blit(img, (MARGIN, 5))

def run_visualizer(initial_state, solution, autoplay=False, show_controls=True, level_id=None):
    pygame.init()
    W_S = sum(UNIT_SIZES) + MARGIN * 2
    screen = pygame.display.set_mode((W_S, W_S + (140 if show_controls else 40)))
    pygame.display.set_caption("Asteroid Escape Solver")
    move_steps = []
    curr = initial_state
    if solution:
        for f, t in solution:
            move_steps.append((curr, (f, t)))
            curr = curr.do_move(f, t)
    move_steps.append((curr, None))
    running, step_idx, anim_start_time, paused, single_step = True, 0, time.time(), not autoplay, False
    while running:
        is_final_state = (step_idx == len(move_steps) - 1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN] and is_final_state: running = False
                elif event.key == pygame.K_SPACE:
                    if paused and step_idx < len(move_steps) - 1: paused, single_step, anim_start_time = False, True, time.time()
                elif event.key == pygame.K_RETURN: paused, single_step = not paused, False; anim_start_time = time.time()
                elif event.key == pygame.K_RIGHT: step_idx, paused, single_step = min(step_idx + 1, len(move_steps) - 1), True, False
                elif event.key == pygame.K_LEFT: step_idx, paused, single_step = max(step_idx - 1, 0), True, False
                elif event.key == pygame.K_r: step_idx, anim_start_time = 0, time.time()
                elif event.key == pygame.K_ESCAPE: running = False
        now = time.time()
        state_before, move = move_steps[step_idx]
        alpha = 0.0
        if move and not paused:
            elapsed = now - anim_start_time
            if elapsed >= TOTAL_STEP_TIME:
                if step_idx < len(move_steps) - 1:
                    step_idx += 1; anim_start_time += TOTAL_STEP_TIME; state_before, move = move_steps[step_idx]; elapsed = now - anim_start_time 
                    if single_step: paused, single_step = True, False
            if move and not paused: alpha = min(1.0, elapsed / ANIMATION_DURATION)
        draw_board(screen, state_before, move, alpha, level_id=level_id)
        img = pygame.font.SysFont(None, 24).render(f"Move {step_idx}/{len(move_steps)-1}{' - SOLVED!' if move_steps[step_idx][0].is_solved() else ''}{' (PAUSED)' if paused else ''}", True, (200, 200, 200))
        screen.blit(img, (MARGIN, W_S + 10))
        if show_controls:
            ctrl_font = pygame.font.SysFont(None, 20)
            controls = ["ENTER: Toggle Auto-play", "SPACE: Animate next step", "RIGHT/LEFT: Jump next/prev", "R: Reset to start", "ESC: Quit"]
            for i, line in enumerate(controls): screen.blit(ctrl_font.render(line, True, (120, 130, 150)), (MARGIN, W_S + 40 + i * 18))
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    pygame.quit()
