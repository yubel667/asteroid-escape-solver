import os
import sys
import numpy as np
import pygame
from PIL import Image
from board_io import parse_board
from board import BoardState
from solver import solve
import visualizer as vis

# Offscreen rendering
os.environ['SDL_VIDEODRIVER'] = 'dummy'

FPS = 24
# Sync with visualizer constants if possible, or define local ones for precise frame counts
ANIM_DUR = 0.4
WAIT_DUR = 0.5
SLIDE_FRAMES = int(ANIM_DUR * FPS)
WAIT_FRAMES = int(WAIT_DUR * FPS)

def surface_to_pil(surface):
    raw_str = pygame.image.tostring(surface, "RGB")
    return Image.frombytes("RGB", surface.get_size(), raw_str)

def export_webp(problem_id):
    pygame.init()
    
    try:
        initial_state = parse_board(problem_id)
    except Exception as e:
        print(f"Error loading {problem_id}: {e}")
        return

    print(f"Solving {problem_id}...")
    solution, visited, duration = solve(initial_state)
    if solution is None:
        print("No solution found.")
        return

    print(f"Solution found in {len(solution)} moves. Generating frames...")

    W_S = sum(vis.UNIT_SIZES) + vis.MARGIN * 2
    surface = pygame.Surface((W_S, W_S + 40))
    font = pygame.font.SysFont(None, 24)
    
    frames = []
    curr_state = initial_state
    
    def draw_frame(state, move_info, alpha, step_idx):
        vis.draw_board(surface, state, move_info=move_info, alpha=alpha, level_id=problem_id)
        # Draw Status
        status = f"Move {step_idx}/{len(solution)}"
        if state.is_solved(): status += " - SOLVED!"
        img = font.render(status, True, (200, 200, 200))
        surface.blit(img, (vis.MARGIN, W_S + 10))
        frames.append(surface_to_pil(surface))

    # 1. Initial pause
    for _ in range(FPS):
        draw_frame(curr_state, None, 0.0, 0)

    for move_idx, (f, t) in enumerate(solution):
        # 2. Animation frames
        for i in range(SLIDE_FRAMES):
            alpha = i / float(SLIDE_FRAMES)
            draw_frame(curr_state, (f, t), alpha, move_idx)
        
        # Update state
        curr_state = curr_state.do_move(f, t)
        
        # 3. Wait frames (Static state after move)
        for _ in range(WAIT_FRAMES):
            draw_frame(curr_state, None, 0.0, move_idx + 1)
        
        print(f"  Processed move {move_idx + 1}/{len(solution)}")

    # 4. Final pause
    for _ in range(FPS * 2):
        draw_frame(curr_state, None, 0.0, len(solution))

    # Save
    os.makedirs("solutions", exist_ok=True)
    out_path = f"solutions/{problem_id}.webp"
    
    # WebP saving with Pillow
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        quality=80,
        method=6 # Best compression
    )
    
    print(f"Exported to {out_path}")
    pygame.quit()

if __name__ == "__main__":
    problem_id = sys.argv[1] if len(sys.argv) > 1 else "01"
    export_webp(problem_id)
