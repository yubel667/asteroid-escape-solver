import pygame
import sys
import time
import os
import numpy as np
from board import PIECES, BoardSetup, BoardState
from board_io import parse_board, serialize_board
import visualizer as vis

# UI Constants
SIDEBAR_WIDTH = 200
EDITOR_WIDTH = sum(vis.UNIT_SIZES) + vis.MARGIN * 2
WINDOW_WIDTH = EDITOR_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = EDITOR_WIDTH + 40

class LevelEditor:
    def __init__(self, problem_id):
        self.problem_id = problem_id
        self.file_path = f"questions/{problem_id}.txt"
        self.piece_pool_types = [0, 1, 1, 1, 2, 3, 4, 5]
        self.current_pieces = []
        for tid in self.piece_pool_types:
            p = next(p for p in PIECES if p.piece_id == tid)
            self.current_pieces.append(p)
        self.board_layout = np.full((3, 3), -1, dtype=int)
        self.dragging_idx = None 
        if os.path.exists(self.file_path):
            try:
                state = parse_board(problem_id)
                pool_slots_available = list(range(8))
                for tj in range(3):
                    for ti in range(3):
                        pid_in_state = state.board[tj, ti]
                        if pid_in_state < 8:
                            piece = state.setup.pieces[pid_in_state]
                            for slot_idx in pool_slots_available:
                                if self.current_pieces[slot_idx].piece_id == piece.piece_id:
                                    self.current_pieces[slot_idx] = piece
                                    self.board_layout[tj, ti] = slot_idx
                                    pool_slots_available.remove(slot_idx)
                                    break
            except Exception as e:
                print(f"Error loading level: {e}")

    def is_piece_free(self, idx):
        return idx not in self.board_layout

    def get_piece_sidebar_pos(self, idx):
        row, col = idx // 2, idx % 2
        return EDITOR_WIDTH + 30 + col * 80, 50 + row * 80

    def check_valid(self):
        placed_slots = []
        for tj in range(3):
            for ti in range(3):
                slot_idx = self.board_layout[tj, ti]
                if slot_idx != -1:
                    placed_slots.append((tj, ti, slot_idx))
        if len(placed_slots) < 8:
            return False, f"Placed {len(placed_slots)}/8 pieces"
        setup_pieces = [self.current_pieces[slot_idx] for _, _, slot_idx in placed_slots]
        setup = BoardSetup(setup_pieces)
        board_indices = np.full((3, 3), 8, dtype=np.int8)
        for i, (tj, ti, _) in enumerate(placed_slots):
            board_indices[tj, ti] = i
        state = BoardState(setup, board_indices)
        for i in range(8):
            for j in range(i + 1, 8):
                if state.is_collision(i, 2+placed_slots[i][0]*3, 2+placed_slots[i][1]*3, j, 2+placed_slots[j][0]*3, 2+placed_slots[j][1]*3):
                    return False, "Collision detected!"
        return True, "Ready to save (S)"

    def save(self):
        valid, msg = self.check_valid()
        if not valid: return False, f"Cannot Save: {msg}"
        try:
            placed_pieces = []
            board_indices = np.full((3, 3), 8, dtype=np.int8)
            for tj in range(3):
                for ti in range(3):
                    slot_idx = self.board_layout[tj, ti]
                    if slot_idx != -1:
                        board_indices[tj, ti] = len(placed_pieces)
                        placed_pieces.append(self.current_pieces[slot_idx])
            state = BoardState(BoardSetup(placed_pieces), board_indices)
            os.makedirs("questions", exist_ok=True)
            with open(self.file_path, "w") as f:
                f.write(serialize_board(state))
            return True, f"Saved to {self.file_path}. Exiting..."
        except Exception as e:
            return False, f"Save Error: {e}"

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f"Level Editor - {self.problem_id}")
        clock = pygame.time.Clock()
        save_success_time = None
        status_override = None
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    status_override = None
                    if event.button == 1:
                        found_in_sidebar = False
                        for i in range(8):
                            x, y = self.get_piece_sidebar_pos(i)
                            if pygame.Rect(x, y, 60, 60).collidepoint(mouse_pos):
                                for tj in range(3):
                                    for ti in range(3):
                                        if self.board_layout[tj, ti] == i: self.board_layout[tj, ti] = -1
                                self.dragging_idx = i
                                found_in_sidebar = True
                                break
                        if not found_in_sidebar and mouse_pos[0] < EDITOR_WIDTH:
                            for tj in range(3):
                                for ti in range(3):
                                    bx, by, bw, bh = vis.get_tile_pixel_bounds(tj, ti)
                                    if pygame.Rect(bx, by, bw, bh).collidepoint(mouse_pos):
                                        slot_idx = self.board_layout[tj, ti]
                                        if slot_idx != -1:
                                            self.dragging_idx = slot_idx
                                            self.board_layout[tj, ti] = -1
                    elif event.button == 3:
                        if mouse_pos[0] < EDITOR_WIDTH:
                            for tj in range(3):
                                for ti in range(3):
                                    bx, by, bw, bh = vis.get_tile_pixel_bounds(tj, ti)
                                    if pygame.Rect(bx, by, bw, bh).collidepoint(mouse_pos): self.board_layout[tj, ti] = -1
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging_idx is not None:
                        if mouse_pos[0] < EDITOR_WIDTH:
                            for tj in range(3):
                                for ti in range(3):
                                    bx, by, bw, bh = vis.get_tile_pixel_bounds(tj, ti)
                                    if pygame.Rect(bx, by, bw, bh).collidepoint(mouse_pos):
                                        if self.board_layout[tj, ti] == -1: self.board_layout[tj, ti] = self.dragging_idx
                        self.dragging_idx = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.dragging_idx is not None:
                        p = self.current_pieces[self.dragging_idx]
                        self.current_pieces[self.dragging_idx] = next(c for c in PIECES if c.piece_id == p.piece_id and c.orientation == (p.orientation + 1) % 4)
                    elif event.key == pygame.K_s:
                        success, msg = self.save()
                        status_override = msg
                        if success: save_success_time = time.time()
            if save_success_time and time.time() - save_success_time > 1.0: return
            vis.draw_board_chrome(screen)
            pygame.draw.rect(screen, (25, 28, 38), (EDITOR_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
            cosmos_draw_queue, piece_draw_queue = [], []
            for i, p in enumerate(self.current_pieces):
                if self.dragging_idx == i: continue
                x, y = self.get_piece_sidebar_pos(i)
                scale = 0.3
                tile_size = sum(vis.UNIT_SIZES[1:4]) * scale
                bx, by = x + 30 - tile_size/2, y + 30 - tile_size/2
                bg_color = vis.COSMOS_TILE if self.is_piece_free(i) else tuple(c//3 for c in vis.COSMOS_TILE)
                cosmos_draw_queue.append((bx, by, tile_size, tile_size, scale, bg_color))
                piece_draw_queue.append((PIECES.index(p), y+30, x+30, scale))
            for tj in range(3):
                for ti in range(3):
                    slot_idx = self.board_layout[tj, ti]
                    if slot_idx != -1:
                        p = self.current_pieces[slot_idx]
                        cj, ci = vis.get_tile_pixel_center(tj, ti)
                        bx, by, bw, bh = vis.get_tile_pixel_bounds(tj, ti)
                        cosmos_draw_queue.append((bx+2, by+2, bw-4, bh-4, 1.0, vis.COSMOS_TILE))
                        piece_draw_queue.append((PIECES.index(p), cj, ci, 1.0))
            if self.dragging_idx is not None:
                p = self.current_pieces[self.dragging_idx]
                tile_size = sum(vis.UNIT_SIZES[1:4])
                cosmos_draw_queue.append((mouse_pos[0]-tile_size/2, mouse_pos[1]-tile_size/2, tile_size, tile_size, 1.0, vis.COSMOS_TILE))
                piece_draw_queue.append((PIECES.index(p), mouse_pos[1], mouse_pos[0], 1.0))
            for bx, by, bw, bh, sc, bg_c in cosmos_draw_queue:
                pygame.draw.rect(screen, bg_c, (bx, by, bw, bh), 0, int(12*sc))
                if sc == 1.0: pygame.draw.rect(screen, (max(0, bg_c[0]-10), max(0, bg_c[1]-10), max(0, bg_c[2]-10)), (bx, by, bw, bh), 2, 12)
            for p_idx, cj, ci, sc in piece_draw_queue: vis.draw_piece(screen, None, p_idx, cj, ci, scale=sc)
            if status_override:
                msg, color = status_override, ((0, 255, 120) if "Saved" in status_override else (255, 100, 100))
            else:
                valid, msg = self.check_valid()
                color = (0, 255, 120) if valid else (200, 200, 200)
            img = pygame.font.SysFont(None, 24).render(msg, True, color)
            screen.blit(img, (vis.MARGIN, WINDOW_HEIGHT - 30))
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    problem_id = sys.argv[1] if len(sys.argv) > 1 else "new_level"
    LevelEditor(problem_id).run()
