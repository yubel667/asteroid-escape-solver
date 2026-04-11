import pygame
import sys
import time
from board import BoardState
from board_io import parse_board
from solver import solve

# Colors
BACKGROUND = (15, 17, 26)
GRID_LINE = (35, 40, 55)
TILE_BORDER = (70, 80, 100)
EMPTY = (10, 12, 18)

COLOR_MAP = {
    0: (60, 160, 255),    # Ship (Blue)
    1: (180, 140, 100),   # Small asteroid
    2: (180, 140, 100),
    3: (180, 140, 100),
    4: (140, 100, 80),    # Big asteroid
    5: (140, 100, 80),
}

# Variable grid sizes to make 2x2 look
# 11 units: 0(B), 1(C), 2(M), 3(C), 4(C), 5(M), 6(C), 7(C), 8(M), 9(C), 10(B)
C_SIZE = 60  # Corner quadrants
M_SIZE = 12  # Middle thin bars
B_SIZE = 25  # Board border
UNIT_SIZES = [B_SIZE, C_SIZE, M_SIZE, C_SIZE, C_SIZE, M_SIZE, C_SIZE, C_SIZE, M_SIZE, C_SIZE, B_SIZE]
MARGIN = 30

def get_unit_pos(idx):
    # Returns the start pixel and center pixel of unit idx
    pos = MARGIN
    for i in range(idx):
        pos += UNIT_SIZES[i]
    return pos, pos + UNIT_SIZES[idx] / 2

WINDOW_SIZE = sum(UNIT_SIZES) + MARGIN * 2

def draw_piece(screen, state, tj, ti, pid):
    piece = state.setup.pieces[pid]
    u_cj = 2 + tj * 3
    u_ci = 2 + ti * 3
    color = COLOR_MAP.get(piece.piece_id, (200, 200, 200))

    if piece.is_ship:
        # Center of the center unit in pixels
        _, pix_cj = get_unit_pos(u_cj)
        _, pix_ci = get_unit_pos(u_ci)
        
        # Upward shift for the whole ship
        S_UP = -30

        # Ship always faces Down (Orientation 0)
        # Body at Row -1
        _, by = get_unit_pos(u_cj - 1)
        by += S_UP
        p1x, _ = get_unit_pos(u_ci - 2)
        p2x, _ = get_unit_pos(u_ci + 2)
        p2x += UNIT_SIZES[u_ci + 2]
        pygame.draw.rect(screen, color, (p1x + 4, by + 4, p2x - p1x - 8, UNIT_SIZES[u_cj-1] - 8), 0, 10)
        # Nose at Row +1
        _, ty = get_unit_pos(u_cj + 1)
        ty += UNIT_SIZES[u_cj+1] * 0.45 + S_UP
        pygame.draw.polygon(screen, color, [(pix_ci - 18, by + UNIT_SIZES[u_cj-1]), (pix_ci + 18, by + UNIT_SIZES[u_cj-1]), (pix_ci, ty)])
    else:
        is_big = piece.piece_id in [4, 5]
        if is_big:
            # Single big circle centered on all cells
            sum_x, sum_y = 0, 0
            for cell in piece.cells:
                _, cj = get_unit_pos(u_cj + cell.y)
                _, ci = get_unit_pos(u_ci + cell.x)
                sum_x += ci
                sum_y += cj
            avg_x = sum_x / len(piece.cells)
            avg_y = sum_y / len(piece.cells)
            radius = C_SIZE * 1.1
            pygame.draw.circle(screen, color, (int(avg_x), int(avg_y)), int(radius))
            pygame.draw.circle(screen, (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30)), (int(avg_x), int(avg_y)), int(radius), 3)
        else:
            # Small asteroids: one circle per "quadrant" cell (ignore middle bar cells for center)
            grid_pos = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for cell in piece.cells:
                if (cell.y, cell.x) in grid_pos:
                    _, cy = get_unit_pos(u_cj + cell.y)
                    _, cx = get_unit_pos(u_ci + cell.x)
                    radius = C_SIZE * 0.45
                    pygame.draw.circle(screen, color, (int(cx), int(cy)), int(radius))
                    pygame.draw.circle(screen, (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30)), (int(cx), int(cy)), int(radius), 2)

def draw_board(screen, state: BoardState):
    screen.fill(BACKGROUND)
    
    # Draw units grid lines
    curr = MARGIN
    for size in UNIT_SIZES:
        pygame.draw.line(screen, GRID_LINE, (MARGIN, curr), (MARGIN + sum(UNIT_SIZES), curr), 1)
        pygame.draw.line(screen, GRID_LINE, (curr, MARGIN), (curr, MARGIN + sum(UNIT_SIZES)), 1)
        curr += size
    pygame.draw.line(screen, GRID_LINE, (MARGIN, curr), (MARGIN + sum(UNIT_SIZES), curr), 1)
    pygame.draw.line(screen, GRID_LINE, (curr, MARGIN), (curr, MARGIN + sum(UNIT_SIZES)), 1)

    # Draw Tile boundaries
    for t_idx in [0, 1, 2, 3]:
        # Indices in UNIT_SIZES for tile start/end
        idx = 1 + t_idx * 3 if t_idx < 3 else 10
        pos = MARGIN + sum(UNIT_SIZES[:idx])
        pygame.draw.line(screen, TILE_BORDER, (MARGIN, pos), (MARGIN + sum(UNIT_SIZES), pos), 3)
        pygame.draw.line(screen, TILE_BORDER, (pos, MARGIN), (pos, MARGIN + sum(UNIT_SIZES)), 3)

    # Draw Opening
    start_x = MARGIN + sum(UNIT_SIZES[:4])
    end_x = MARGIN + sum(UNIT_SIZES[:7])
    y_pos = MARGIN + sum(UNIT_SIZES[:10])
    pygame.draw.rect(screen, (0, 255, 120), (start_x, y_pos, end_x - start_x, 10), 0, 5)

    # Draw Pieces
    for tj in range(3):
        for ti in range(3):
            pid = state.board[tj, ti]
            if pid < 8:
                draw_piece(screen, state, tj, ti, pid)

def main():
    pygame.init()
    # Increase height for status bar
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + 40))
    pygame.display.set_caption("Asteroid Escape Solver")
    
    question_num = sys.argv[1] if len(sys.argv) > 1 else "01"
    initial_state = parse_board(question_num)
    
    print("Solving...")
    solution = solve(initial_state)
    if not solution:
        print("No solution found!")
        return

    moves = [initial_state]
    curr = initial_state
    for f, t in solution:
        curr = curr.do_move(f, t)
        moves.append(curr)

    running = True
    move_idx = 0
    last_move_time = time.time()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    move_idx = 0 # Reset
                if event.key == pygame.K_RIGHT:
                    move_idx = min(move_idx + 1, len(moves) - 1)
                if event.key == pygame.K_LEFT:
                    move_idx = max(move_idx - 1, 0)

        # Auto-play
        if move_idx < len(moves) - 1 and time.time() - last_move_time > 1.0:
            move_idx += 1
            last_move_time = time.time()

        draw_board(screen, moves[move_idx])
        
        # Draw status
        font = pygame.font.SysFont(None, 24)
        status = f"Move {move_idx}/{len(moves)-1}"
        if moves[move_idx].is_solved():
            status += " - SOLVED!"
        img = font.render(status, True, (255, 255, 255))
        screen.blit(img, (MARGIN, WINDOW_SIZE - MARGIN + 5))

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
