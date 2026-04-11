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

def draw_piece(screen, state, pid, pix_cj, pix_ci):
    piece = state.setup.pieces[pid]
    color = COLOR_MAP.get(piece.piece_id, (200, 200, 200))
    
    if piece.is_ship:
        S_UP = 0
        body_center_y = pix_cj - (M_SIZE/2 + C_SIZE/2) + S_UP
        p1x = pix_ci - (M_SIZE/2 + C_SIZE + C_SIZE/2)
        p2x = pix_ci + (M_SIZE/2 + C_SIZE + C_SIZE/2)
        bw = p2x - p1x + C_SIZE
        pygame.draw.rect(screen, color, (p1x - C_SIZE/2 + 4, body_center_y - C_SIZE/2 + 4, bw - 8, C_SIZE - 8), 0, 10)
        
        ty = pix_cj + (M_SIZE/2 + C_SIZE/2) * 0.9 + S_UP
        base_y = body_center_y + C_SIZE/2
        pygame.draw.polygon(screen, color, [(pix_ci - 18, base_y), (pix_ci + 18, base_y), (pix_ci, ty + C_SIZE/2)])
    else:
        is_big = piece.piece_id in [4, 5]
        if is_big:
            sum_dx, sum_dy = 0, 0
            for cell in piece.cells:
                dy = 0
                if cell.y == 1: dy = M_SIZE/2 + C_SIZE/2
                elif cell.y == -1: dy = -(M_SIZE/2 + C_SIZE/2)
                elif cell.y == 2: dy = M_SIZE/2 + C_SIZE + C_SIZE/2
                elif cell.y == -2: dy = -(M_SIZE/2 + C_SIZE + C_SIZE/2)
                dx = 0
                if cell.x == 1: dx = M_SIZE/2 + C_SIZE/2
                elif cell.x == -1: dx = -(M_SIZE/2 + C_SIZE/2)
                elif cell.x == 2: dx = M_SIZE/2 + C_SIZE + C_SIZE/2
                elif cell.x == -2: dx = -(M_SIZE/2 + C_SIZE + C_SIZE/2)
                sum_dy += dy
                sum_dx += dx
            avg_cy = pix_cj + sum_dy / len(piece.cells)
            avg_cx = pix_ci + sum_dx / len(piece.cells)
            radius = C_SIZE * 0.9
            pygame.draw.circle(screen, color, (int(avg_cx), int(avg_cy)), int(radius))
            pygame.draw.circle(screen, (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30)), (int(avg_cx), int(avg_cy)), int(radius), 3)
        else:
            grid_pos = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for cell in piece.cells:
                if (cell.y, cell.x) in grid_pos:
                    off_y = (M_SIZE/2 + C_SIZE/2) if cell.y == 1 else -(M_SIZE/2 + C_SIZE/2)
                    off_x = (M_SIZE/2 + C_SIZE/2) if cell.x == 1 else -(M_SIZE/2 + C_SIZE/2)
                    radius = C_SIZE * 0.45
                    pygame.draw.circle(screen, color, (int(pix_ci + off_x), int(pix_cj + off_y)), int(radius))
                    pygame.draw.circle(screen, (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30)), (int(pix_ci + off_x), int(pix_cj + off_y)), int(radius), 2)

def draw_board(screen, state: BoardState, move_info=None, alpha=0.0):
    screen.fill(BACKGROUND)
    curr = MARGIN
    for size in UNIT_SIZES:
        pygame.draw.line(screen, GRID_LINE, (MARGIN, curr), (MARGIN + sum(UNIT_SIZES), curr), 1)
        pygame.draw.line(screen, GRID_LINE, (curr, MARGIN), (curr, MARGIN + sum(UNIT_SIZES)), 1)
        curr += size
    pygame.draw.line(screen, GRID_LINE, (MARGIN, curr), (MARGIN + sum(UNIT_SIZES), curr), 1)
    pygame.draw.line(screen, GRID_LINE, (curr, MARGIN), (curr, MARGIN + sum(UNIT_SIZES)), 1)
    for t_idx in [0, 1, 2, 3]:
        idx = 1 + t_idx * 3 if t_idx < 3 else 10
        pos = MARGIN + sum(UNIT_SIZES[:idx])
        pygame.draw.line(screen, TILE_BORDER, (MARGIN, pos), (MARGIN + sum(UNIT_SIZES), pos), 3)
        pygame.draw.line(screen, TILE_BORDER, (pos, MARGIN), (pos, MARGIN + sum(UNIT_SIZES)), 3)
    start_x = MARGIN + sum(UNIT_SIZES[:4])
    end_x = MARGIN + sum(UNIT_SIZES[:7])
    y_pos = MARGIN + sum(UNIT_SIZES[:10])
    pygame.draw.rect(screen, (0, 255, 120), (start_x, y_pos, end_x - start_x, 10), 0, 5)
    moving_f, moving_t = move_info if move_info else (None, None)
    piece_draw_data = [] 
    ship_pid = next((i for i, p in enumerate(state.setup.pieces) if p.is_ship), None)
    ship_rendered = False
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
                    offset = 132
                    target_cj, target_ci = cj + offset, ci
                    target_by, target_bx = by + offset, bx
                else:
                    target_cj, target_ci = get_tile_pixel_center(target_j, target_i)
                    target_bx, target_by, _, _ = get_tile_pixel_bounds(target_j, target_i)
                cur_cj = cj + (target_cj - cj) * alpha
                cur_ci = ci + (target_ci - ci) * alpha
                cur_bx = bx + (target_bx - bx) * alpha
                cur_by = by + (target_by - by) * alpha
                if pid == ship_pid: ship_rendered = True
            else:
                cur_cj, cur_ci = cj, ci
                cur_bx, cur_by = bx, by
            pygame.draw.rect(screen, COSMOS_TILE, (cur_bx + 2, cur_by + 2, bw - 4, bh - 4), 0, 12)
            pygame.draw.rect(screen, (max(0, COSMOS_TILE[0]-10), max(0, COSMOS_TILE[1]-10), max(0, COSMOS_TILE[2]-10)), (cur_bx + 2, cur_by + 2, bw - 4, bh - 4), 2, 12)
            piece_draw_data.append((pid, cur_cj, cur_ci))
    if not ship_rendered and ship_pid is not None:
        cj, ci = get_tile_pixel_center(2, 1)
        bx, by, bw, bh = get_tile_pixel_bounds(2, 1)
        offset = 132
        cur_cj, cur_ci = cj + offset, ci
        cur_bx, cur_by = bx, by + offset
        pygame.draw.rect(screen, COSMOS_TILE, (cur_bx + 2, cur_by + 2, bw - 4, bh - 4), 0, 12)
        pygame.draw.rect(screen, (max(0, COSMOS_TILE[0]-10), max(0, COSMOS_TILE[1]-10), max(0, COSMOS_TILE[2]-10)), (cur_bx + 2, cur_by + 2, bw - 4, bh - 4), 2, 12)
        piece_draw_data.append((ship_pid, cur_cj, cur_ci))
    for pid, cur_cj, cur_ci in piece_draw_data:
        draw_piece(screen, state, pid, cur_cj, cur_ci)

def run_visualizer(initial_state, solution):
    pygame.init()
    W_S = sum(UNIT_SIZES) + MARGIN * 2
    screen = pygame.display.set_mode((W_S, W_S + 40))
    pygame.display.set_caption("Asteroid Escape Solver")
    move_steps = []
    curr = initial_state
    if solution:
        for f, t in solution:
            move_steps.append((curr, (f, t)))
            curr = curr.do_move(f, t)
    move_steps.append((curr, None))
    running = True
    step_idx = 0
    anim_start_time = time.time()
    paused = True # Default to not auto play
    single_step = False
    
    while running:
        is_final_state = (step_idx == len(move_steps) - 1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN] and is_final_state:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if step_idx < len(move_steps) - 1:
                        paused = False
                        single_step = True
                        anim_start_time = time.time()
                elif event.key == pygame.K_RETURN:
                    paused = not paused
                    single_step = False
                    if not paused: anim_start_time = time.time()
                elif event.key == pygame.K_RIGHT:
                    step_idx = min(step_idx + 1, len(move_steps) - 1)
                    paused = True
                    single_step = False
                elif event.key == pygame.K_LEFT:
                    step_idx = max(step_idx - 1, 0)
                    paused = True
                    single_step = False
                elif event.key == pygame.K_r:
                    step_idx = 0
                    anim_start_time = time.time()

        now = time.time()
        state_before, move = move_steps[step_idx]
        
        alpha = 0.0
        if move and not paused:
            elapsed = now - anim_start_time
            if elapsed >= TOTAL_STEP_TIME:
                if step_idx < len(move_steps) - 1:
                    step_idx += 1
                    anim_start_time += TOTAL_STEP_TIME # Maintain timing continuity
                    state_before, move = move_steps[step_idx]
                    elapsed = now - anim_start_time # Recalculate for the new move
                    if single_step:
                        paused = True
                        single_step = False
            
            # Recalculate alpha for the frame
            if move and not paused:
                alpha = min(1.0, elapsed / ANIMATION_DURATION)
            else:
                alpha = 0.0

        draw_board(screen, state_before, move, alpha)
        font = pygame.font.SysFont(None, 24)
        status = f"Move {step_idx}/{len(move_steps)-1}"
        if move_steps[step_idx][0].is_solved(): status += " - SOLVED!"
        if paused: status += " (PAUSED)"
        img = font.render(status, True, (200, 200, 200))
        screen.blit(img, (MARGIN, W_S + 10))
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    pygame.quit()
