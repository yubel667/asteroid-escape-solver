import pygame
import sys
import time
from board import BoardState
from board_io import parse_board
from solver import solve

# Colors
BACKGROUND = (30, 30, 30)
GRID_LINE = (50, 50, 50)
TILE_BORDER = (100, 100, 100)
EMPTY = (20, 20, 20)

COLOR_MAP = {
    0: (0, 120, 255),    # Ship (Blue)
    1: (150, 75, 0),     # Small asteroid (Brown)
    2: (180, 100, 30),   # Asteroid pair
    3: (160, 120, 40),   # Asteroid pair edge
    4: (100, 100, 100),  # Big asteroid
    5: (120, 120, 120),  # Big asteroid edge
}

UNIT_SIZE = 40
GRID_COUNT = 11
MARGIN = 20
WINDOW_SIZE = UNIT_SIZE * GRID_COUNT + MARGIN * 2

def draw_board(screen, state: BoardState):
    screen.fill(BACKGROUND)
    
    # Draw grid
    for i in range(GRID_COUNT + 1):
        pygame.draw.line(screen, GRID_LINE, (MARGIN, MARGIN + i * UNIT_SIZE), (MARGIN + GRID_COUNT * UNIT_SIZE, MARGIN + i * UNIT_SIZE))
        pygame.draw.line(screen, GRID_LINE, (MARGIN + i * UNIT_SIZE, MARGIN), (MARGIN + i * UNIT_SIZE, MARGIN + GRID_COUNT * UNIT_SIZE))

    # Draw Tile boundaries (3x3 tiles)
    for i in range(4):
        width = 3 if i in [0, 3] else 1
        pygame.draw.line(screen, TILE_BORDER, (MARGIN, MARGIN + (1 + i * 3) * UNIT_SIZE), (MARGIN + GRID_COUNT * UNIT_SIZE, MARGIN + (1 + i * 3) * UNIT_SIZE), width)
        pygame.draw.line(screen, TILE_BORDER, (MARGIN + (1 + i * 3) * UNIT_SIZE, MARGIN), (MARGIN + (1 + i * 3) * UNIT_SIZE, MARGIN + GRID_COUNT * UNIT_SIZE), width)

    # Draw Opening (Exit at bottom middle)
    # Tile (2,1) bottom is at j=3. Unit center of opening is (10, 5) approx?
    # Actually, goal_tile is (3, 1). Center is j=2+3*3=11, i=2+1*3=5.
    # Unit coords (11, 4), (11, 5), (11, 6) are outside.
    # We can highlight the boundary at (10, 4)-(10, 6)
    pygame.draw.rect(screen, (0, 255, 0), (MARGIN + 4 * UNIT_SIZE, MARGIN + 10 * UNIT_SIZE, 3 * UNIT_SIZE, 5), 0)

    # Draw Pieces
    # Occupancy map logic
    occupancy = {} # (y, x) -> color
    for tj in range(3):
        for ti in range(3):
            pid = state.board[tj, ti]
            if pid == 8: continue
            
            piece = state.setup.pieces[pid]
            center_j = 2 + tj * 3
            center_i = 2 + ti * 3
            color = COLOR_MAP.get(piece.piece_id, (200, 200, 200))
            
            for cell in piece.cells:
                yj = center_j + cell.y
                xi = center_i + cell.x
                if 0 <= yj < GRID_COUNT and 0 <= xi < GRID_COUNT:
                    occupancy[(yj, xi)] = color
                elif piece.is_ship: # Ship exiting
                    occupancy[(yj, xi)] = color

    for (yj, xi), color in occupancy.items():
        if 0 <= yj < GRID_COUNT and 0 <= xi < GRID_COUNT:
            pygame.draw.rect(screen, color, (MARGIN + xi * UNIT_SIZE + 2, MARGIN + yj * UNIT_SIZE + 2, UNIT_SIZE - 4, UNIT_SIZE - 4), 0, 4)

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
