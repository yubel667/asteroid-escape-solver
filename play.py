import pygame
import sys
import time
import subprocess
import json
from board import BoardState
from board_io import parse_board, serialize_board
from solver import solve
import visualizer as vis

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 play.py <level_id>")
        return
    
    level_id = sys.argv[1]
    try:
        initial_state = parse_board(level_id)
    except Exception as e:
        print(f"Error loading level {level_id}: {e}")
        return

    pygame.init()
    W_S = sum(vis.UNIT_SIZES) + vis.MARGIN * 2
    screen = pygame.display.set_mode((W_S, W_S + 140))
    pygame.display.set_caption(f"Asteroid Escape - Play Level {level_id}")
    clock = pygame.time.Clock()

    current_state = initial_state
    move_info = None # (from_pos, to_pos)
    anim_start_time = 0
    is_animating = False
    is_illegal_anim = False
    
    hint_msg = ""
    hint_msg_time = 0
    
    solve_proc = None
    cached_solution = [] # List of {"from": (j,i), "to": (j,i)}
    
    # Pre-create overlay surface to avoid per-frame creation
    overlay = pygame.Surface((W_S, W_S), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    
    ANIM_DUR = 0.2
    ILLEGAL_ANIM_DUR = 0.3

    running = True
    while running:
        now = time.time()
        
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    current_state = initial_state
                    move_info = None
                    is_animating = False
                    cached_solution = []
                elif event.key == pygame.K_h and not is_animating and not current_state.is_solved() and not solve_proc:
                    if cached_solution:
                        # Use next move from cache
                        move = cached_solution.pop(0)
                        move_info = (tuple(move['from']), tuple(move['to']))
                        hint_msg = f"Moves left: {len(cached_solution) + 1}"
                        hint_msg_time = now
                        anim_start_time = now
                        is_animating = True
                        is_illegal_anim = False
                    else:
                        # Start solver in a separate process
                        board_content = serialize_board(current_state)
                        try:
                            solve_proc = subprocess.Popen(
                                [sys.executable, "solver.py", "-"],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            solve_proc.stdin.write(board_content)
                            solve_proc.stdin.close()
                            solve_proc.stdin = None # Prevent communicate() from flushing closed pipe
                        except (IOError, BrokenPipeError) as e:
                            print(f"Failed to start solver: {e}")
                            solve_proc = None
                            hint_msg = "Solver Failed!"
                            hint_msg_time = now
                elif not is_animating and not current_state.is_solved() and not solve_proc:
                    # 1. Special case: ship exit prioritization (VALID move only here)
                    ship_pos = None
                    for tj in range(3):
                        for ti in range(3):
                            pid = current_state.board[tj, ti]
                            if pid < 8 and current_state.setup.pieces[pid].is_ship:
                                ship_pos = (tj, ti)
                                break
                    
                    if ship_pos == (2, 1) and event.key == pygame.K_DOWN:
                        if current_state.can_slide(2, 1, 3, 1):
                            move_info = ((2, 1), (3, 1))
                            anim_start_time = now
                            is_animating = True
                            is_illegal_anim = False
                            cached_solution = []
                    
                    if not is_animating:
                        # 2. Normal move towards empty spot (Valid or Illegal)
                        ej, ei = current_state.get_empty_pos()
                        from_pos = None
                        to_pos = (ej, ei)
                        
                        if event.key == pygame.K_UP:
                            from_pos = (ej + 1, ei)
                        elif event.key == pygame.K_DOWN:
                            from_pos = (ej - 1, ei)
                        elif event.key == pygame.K_LEFT:
                            from_pos = (ej, ei + 1)
                        elif event.key == pygame.K_RIGHT:
                            from_pos = (ej, ei - 1)
                        
                        if from_pos:
                            fj, fi = from_pos
                            # Check if within bounds and NOT empty
                            if 0 <= fj < 3 and 0 <= fi < 3:
                                piece_id = current_state.board[fj, fi]
                                if piece_id != 8:
                                    # Candidate piece found
                                    if current_state.can_slide(fj, fi, ej, ei):
                                        move_info = (from_pos, to_pos)
                                        anim_start_time = now
                                        is_animating = True
                                        is_illegal_anim = False
                                        cached_solution = [] # Manual move invalidates cache
                                    else:
                                        # Illegal move towards empty space
                                        move_info = (from_pos, to_pos)
                                        anim_start_time = now
                                        is_animating = True
                                        is_illegal_anim = True
                    
                    if not is_animating and ship_pos == (2, 1) and event.key == pygame.K_DOWN:
                        # 3. If no other move was possible, show illegal exit attempt for ship
                        move_info = ((2, 1), (3, 1))
                        anim_start_time = now
                        is_animating = True
                        is_illegal_anim = True

        if solve_proc:
            if solve_proc.poll() is not None:
                # Solve complete
                stdout, stderr = solve_proc.communicate()
                try:
                    result = json.loads(stdout.strip())
                    if isinstance(result, dict) and "error" in result:
                        hint_msg = "No solution found!"
                    else:
                        # result is a list of moves
                        cached_solution = result
                        if cached_solution:
                            move = cached_solution.pop(0)
                            hint_msg = f"Moves left: {len(cached_solution) + 1}"
                            move_info = (tuple(move['from']), tuple(move['to']))
                            anim_start_time = time.time()
                            is_animating = True
                            is_illegal_anim = False
                except Exception as e:
                    print(f"Error parsing solver output: {e}\nSTDOUT: {stdout}\nSTDERR: {stderr}")
                    hint_msg = "Solver Error!"
                
                hint_msg_time = time.time()
                solve_proc = None
            else:
                # Still solving
                pass

        # 2. Update Animation
        alpha = 0.0
        if is_animating:
            elapsed = now - anim_start_time
            if is_illegal_anim:
                if elapsed >= ILLEGAL_ANIM_DUR:
                    is_animating = False
                    move_info = None
                else:
                    # Slide to 20% and back
                    half = ILLEGAL_ANIM_DUR / 2
                    if elapsed < half:
                        alpha = (elapsed / half) * 0.2
                    else:
                        alpha = 0.2 - ((elapsed - half) / half) * 0.2
            else:
                if elapsed >= ANIM_DUR:
                    is_animating = False
                    current_state = current_state.do_move(move_info[0], move_info[1])
                    move_info = None
                else:
                    alpha = elapsed / ANIM_DUR

        # 3. Draw
        vis.draw_board(screen, current_state, move_info=move_info, alpha=alpha, level_id=level_id)
        
        # Status text
        status = "SOLVED!" if current_state.is_solved() else "Playing..."
        img = pygame.font.SysFont(None, 24).render(status, True, (200, 200, 200))
        screen.blit(img, (vis.MARGIN, W_S + 10))
        
        # Hint message (briefly show)
        if hint_msg and now - hint_msg_time < 2.0:
            hint_img = pygame.font.SysFont(None, 24, bold=True).render(hint_msg, True, (255, 255, 100))
            screen.blit(hint_img, (W_S - vis.MARGIN - hint_img.get_width(), W_S + 10))
        
        if solve_proc:
            # SOLVING Overlay
            screen.blit(overlay, (0, 0))
            solve_font = pygame.font.SysFont(None, 48, bold=True)
            solve_img = solve_font.render("SOLVING...", True, (255, 255, 255))
            screen.blit(solve_img, solve_img.get_rect(center=(W_S // 2, W_S // 2)))

        ctrl_font = pygame.font.SysFont(None, 20)
        controls = ["ARROWS: Move Pieces", "H: Play next hint step (Step-by-step)", "R: Reset Level", "ESC: Quit"]
        for i, line in enumerate(controls):
            screen.blit(ctrl_font.render(line, True, (120, 130, 150)), (vis.MARGIN, W_S + 40 + i * 18))
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
