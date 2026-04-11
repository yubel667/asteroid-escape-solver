import pygame
import sys
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
        
        self.board_layout = np.full((3, 3), None, dtype=object)
        self.dragging_idx = None 
        
        if os.path.exists(self.file_path):
            try:
                state = parse_board(problem_id)
                pool_copy = list(range(8))
                for tj in range(3):
                    for ti in range(3):
                        pid_in_state = state.board[tj, ti]
                        if pid_in_state < 8:
                            piece = state.setup.pieces[pid_in_state]
                            for i in pool_copy:
                                if self.current_pieces[i].piece_id == piece.piece_id:
                                    self.current_pieces[i] = piece
                                    self.board_layout[tj, ti] = self.current_pieces[i]
                                    pool_copy.remove(i)
                                    break
            except Exception as e:
                print(f"Error loading level: {e}")

    def is_piece_free(self, idx):
        p = self.current_pieces[idx]
        for tj in range(3):
            for ti in range(3):
                if self.board_layout[tj, ti] == p: return False
        return True

    def get_piece_sidebar_pos(self, idx):
        row, col = idx // 2, idx % 2
        return EDITOR_WIDTH + 30 + col * 80, 50 + row * 80

    def check_valid(self):
        placed = []
        for tj in range(3):
            for ti in range(3):
                if self.board_layout[tj, ti]:
                    placed.append((tj, ti, self.board_layout[tj, ti]))
        
        if len(placed) < 8:
            return False, f"Placed {len(placed)}/8 pieces"
        
        # Collision check
        setup = BoardSetup([p for tj, ti, p in placed])
        board_indices = np.full((3, 3), 8, dtype=np.int8)
        for idx, (tj, ti, p) in enumerate(placed):
            board_indices[tj, ti] = idx
        state = BoardState(setup, board_indices)
        
        for i in range(8):
            for j in range(i + 1, 8):
                tj1, ti1, _ = placed[i]
                tj2, ti2, _ = placed[j]
                if state.is_collision(i, 2+tj1*3, 2+ti1*3, j, 2+tj2*3, 2+ti2*3):
                    return False, "Collision detected!"
        return True, "Ready to save (S)"

    def save(self):
        valid, msg = self.check_valid()
        if not valid: return
        placed = []
        board_indices = np.full((3, 3), 8, dtype=np.int8)
        for tj in range(3):
            for ti in range(3):
                p = self.board_layout[tj, ti]
                if p:
                    board_indices[tj, ti] = len(placed)
                    placed.append(p)
        state = BoardState(BoardSetup(placed), board_indices)
        with open(self.file_path, "w") as f:
            f.write(serialize_board(state))
        print(f"Saved to {self.file_path}")

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f"Level Editor - {self.problem_id}")
        clock = pygame.time.Clock()
        
        while True:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Sidebar
                        for i in range(8):
                            x, y = self.get_piece_sidebar_pos(i)
                            if pygame.Rect(x, y, 60, 60).collidepoint(mouse_pos):
                                for tj in range(3):
                                    for ti in range(3):
                                        if self.board_layout[tj, ti] == self.current_pieces[i]:
                                            self.board_layout[tj, ti] = None
                                self.dragging_idx = i
                                break
                        # Board
                        if mouse_pos[0] < EDITOR_WIDTH:
                            for tj in range(3):
                                for ti in range(3):
                                    bx, by, bw, bh = vis.get_tile_pixel_bounds(tj, ti)
                                    if pygame.Rect(bx, by, bw, bh).collidepoint(mouse_pos):
                                        p = self.board_layout[tj, ti]
                                        if p:
                                            self.dragging_idx = next(i for i, cp in enumerate(self.current_pieces) if cp == p)
                                            self.board_layout[tj, ti] = None
                    elif event.button == 3:
                        for tj in range(3):
                            for ti in range(3):
                                bx, by, bw, bh = vis.get_tile_pixel_bounds(tj, ti)
                                if pygame.Rect(bx, by, bw, bh).collidepoint(mouse_pos):
                                    self.board_layout[tj, ti] = None
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragging_idx is not None:
                        placed = False
                        if mouse_pos[0] < EDITOR_WIDTH:
                            for tj in range(3):
                                for ti in range(3):
                                    bx, by, bw, bh = vis.get_tile_pixel_bounds(tj, ti)
                                    if pygame.Rect(bx, by, bw, bh).collidepoint(mouse_pos):
                                        if self.board_layout[tj, ti] is None:
                                            self.board_layout[tj, ti] = self.current_pieces[self.dragging_idx]
                                            placed = True
                        self.dragging_idx = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.dragging_idx is not None:
                        p = self.current_pieces[self.dragging_idx]
                        self.current_pieces[self.dragging_idx] = next(c for c in PIECES if c.piece_id == p.piece_id and c.orientation == (p.orientation + 1) % 4)
                    elif event.key == pygame.K_s: self.save()

            vis.draw_board_chrome(screen)
            # Sidebar
            pygame.draw.rect(screen, (25, 28, 38), (EDITOR_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
            for i, p in enumerate(self.current_pieces):
                if self.dragging_idx == i: continue
                x, y = self.get_piece_sidebar_pos(i)
                color = vis.COLOR_MAP.get(p.piece_id, (200, 200, 200))
                is_free = self.is_piece_free(i)
                # Cosmos tile background for sidebar (scaled)
                scale = 0.3
                bw, bh = sum(vis.UNIT_SIZES[1:4])*scale, sum(vis.UNIT_SIZES[1:4])*scale
                bx, by = x + 30 - bw/2, y + 30 - bh/2
                bg_color = vis.COSMOS_TILE if is_free else tuple(c//3 for c in vis.COSMOS_TILE)
                pygame.draw.rect(screen, bg_color, (bx, by, bw, bh), 0, int(12*scale))
                # Piece icon
                vis.draw_piece(screen, None, PIECES.index(p), y+30, x+30, scale=scale)
            
            # Board pieces
            for tj in range(3):
                for ti in range(3):
                    p = self.board_layout[tj, ti]
                    if p:
                        cj, ci = vis.get_tile_pixel_center(tj, ti)
                        bx, by, bw, bh = vis.get_tile_pixel_bounds(tj, ti)
                        pygame.draw.rect(screen, vis.COSMOS_TILE, (bx+2, by+2, bw-4, bh-4), 0, 12)
                        pygame.draw.rect(screen, (max(0, vis.COSMOS_TILE[0]-10), max(0, vis.COSMOS_TILE[1]-10), max(0, vis.COSMOS_TILE[2]-10)), (bx + 2, by + 2, bw - 4, bh - 4), 2, 12)
                        vis.draw_piece(screen, None, PIECES.index(p), cj, ci)
            
            if self.dragging_idx is not None:
                p = self.current_pieces[self.dragging_idx]
                # Draw cosmos background for ghost
                bw, bh = sum(vis.UNIT_SIZES[1:4]), sum(vis.UNIT_SIZES[1:4])
                pygame.draw.rect(screen, vis.COSMOS_TILE, (mouse_pos[0]-bw/2, mouse_pos[1]-bh/2, bw, bh), 0, 12)
                vis.draw_piece(screen, None, PIECES.index(p), mouse_pos[1], mouse_pos[0])

            valid, msg = self.check_valid()
            font = pygame.font.SysFont(None, 24)
            img = font.render(msg, True, (0, 255, 0) if valid else (255, 100, 100))
            screen.blit(img, (vis.MARGIN, WINDOW_HEIGHT - 30))
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    problem_id = sys.argv[1] if len(sys.argv) > 1 else "new_level"
    LevelEditor(problem_id).run()
