import numpy as np
from typing import List

# A location on the board.
class Loc:
    def __init__(self, y, x):
        self.y = y
        self.x = x

    # rotate 90 degrees clockwise.
    def rotate(self) -> "Loc":
        return Loc(self.x, -self.y)


# A generic Piece
class Piece:
    # relative to the center board, the occupacy of each cell that uses space.
    # type_id does not reflect its orientation. in the puzzle there's no need to change orientation.
    def __init__(self, piece_id, cells: List[Loc], orientation: bool, repr_str: str, is_ship=False):
        self.piece_id = piece_id
        # cells are for collision detection. each tile is a 3x3 grid, we use 0,0 as the center.
        # for example the ship is like this (The center C is (0,0) of the tile) the ship extend far
        # back to its left and right side, and extrude in the middle as well.
        # OOXOO
        #  XCX
        #  XOX
        self.cells = cells
        self.orientation = orientation
        assert len(repr_str) == 4
        # repr_str format: 
        #  12
        #  43
        self.repr_str = repr_str
        self.repr_char = repr_str.strip()[0] # Used for debug string.
        self.is_ship = is_ship

    def rotate(self) -> "Piece":
        new_cells = [
            cell.rotate() for cell in self.cells
        ]
        # rotate the repr clockwise: s3 s0 s1 s2
        repr_str = self.repr_str[3:4] + self.repr_str[0:3]
        new_orientation = (self.orientation + 1) % 4
        return Piece(self.piece_id, new_cells, new_orientation, repr_str, self.is_ship)

def build_pieces():
    pieces = []
    # Ship
    pieces.append(Piece(0, [
            Loc(1,0),
            Loc(-1, -2),
            Loc(-1, -1),
            Loc(-1, 1),
            Loc(-1, 2)
        ], 0, "SS  ", is_ship = True))
    # one small astroid
    piece = Piece(1, [Loc(-1, -1)], 0, "a   ")
    for i in range(4):
        pieces.append(piece)
        piece = piece.rotate()
    # two small astroids side-by-side
    piece = Piece(2, [Loc(-1, -1), Loc(1,1)], 0, "a a ")
    pieces.append(piece)
    piece = piece.rotate()
    pieces.append(piece)
    # two small astroids on same edge
    piece = Piece(3, [Loc(-1, -1), Loc(-1,1)], 0, "aa  ")
    for i in range(4):
        pieces.append(piece)
        piece = piece.rotate()
    # big astroid in corner
    piece = Piece(4, [Loc(-1, -1), Loc(-2, -1), Loc(-1, -2), Loc(-2,-2)],0, "A   ")
    for i in range(4):
        pieces.append(piece)
        piece = piece.rotate()
    # big astroid at edge
    piece = Piece(5, [Loc(-1, -1), Loc(-1, 0), Loc(-1, 1), Loc(-2, -1), Loc(-2, 0), Loc(-2,1)], 0, "AA  ")
    for i in range(4):
        pieces.append(piece)
        piece = piece.rotate()
    return pieces
# all potential pieces
PIECES = build_pieces()


class BoardSetup:
    # in total 8 pieces, three of type 1 and other piece 1 each.
    EXPECTED_PIECE_SET = [0, 1, 1, 1, 2, 3, 4, 5]
    def __init__(self, pieces: List[Piece]):
        self.pieces = pieces
        piece_ids = [p.piece_id for p in pieces]
        piece_ids.sort()
        assert len(self.pieces) == 8
        for i in range(8):
            assert piece_ids[i] == self.EXPECTED_PIECE_SET[i]


class BoardState:
    def __init__(self, setup: BoardSetup, board: np.array):
        self.setup = setup
        # Board is an np.int array of shape (3,3).
        # each number corresponds to setup.piece[i], or 8 for the empty space
        self.board = board
        # Check that board is valid.
        assert self.board.shape == (3,3)

    def get_piece_id_at(self, j, i):
        return self.board[j, i]

    def get_empty_pos(self):
        pos = np.where(self.board == 8)
        return int(pos[0][0]), int(pos[1][0])

    def get_unit_cells(self, piece_id, center_j, center_i):
        # center_j, center_i are unit coordinates.
        # tile (tj, ti) has center at (2 + tj*3, 2 + ti*3)
        piece = self.setup.pieces[piece_id]
        return [(center_j + cell.y, center_i + cell.x) for cell in piece.cells]

    def is_collision(self, piece1_id, center1_j, center1_i, piece2_id, center2_j, center2_i):
        cells1 = self.get_unit_cells(piece1_id, center1_j, center1_i)
        cells2 = self.get_unit_cells(piece2_id, center2_j, center2_i)
        # Check intersection
        set1 = set(cells1)
        for c in cells2:
            if c in set1:
                return True
        return False

    def can_slide(self, from_j, from_i, to_j, to_i):
        # Piece at (from_j, from_i) slides to (to_j, to_i).
        # (to_j, to_i) must be adjacent and empty.
        if not (0 <= to_j < 3 and 0 <= to_i < 3):
            # Only ship can slide off board.
            piece_id = self.board[from_j, from_i]
            if not self.setup.pieces[piece_id].is_ship:
                return False
            # Opening at bottom middle (3, 1)
            if not (to_j == 3 and to_i == 1):
                return False
        
        if abs(from_j - to_j) + abs(from_i - to_i) != 1:
            return False
        
        piece_id = self.board[from_j, from_i]
        
        # Intermediate unit steps.
        # From center (2+from_j*3, 2+from_i*3) to (2+to_j*3, 2+to_i*3)
        start_cj = 2 + from_j * 3
        start_ci = 2 + from_i * 3
        end_cj = 2 + to_j * 3
        end_ci = 2 + to_i * 3
        
        dj = to_j - from_j
        di = to_i - from_i
        
        # Check steps 1, 2, 3
        for step in range(1, 4):
            curr_cj = start_cj + step * dj
            curr_ci = start_ci + step * di
            
            # Check collision with all OTHER pieces currently on board.
            for tj in range(3):
                for ti in range(3):
                    if (tj, ti) == (from_j, from_i):
                        continue
                    other_piece_id = self.board[tj, ti]
                    if other_piece_id == 8:
                        continue
                    
                    other_cj = 2 + tj * 3
                    other_ci = 2 + ti * 3
                    
                    if self.is_collision(piece_id, curr_cj, curr_ci, other_piece_id, other_cj, other_ci):
                        return False
        return True

    def get_possible_moves(self, goal_tile=(3, 1)):
        moves = []
        ej, ei = self.get_empty_pos()
        # Pieces that can move into the empty spot.
        for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            pj, pi = ej - dj, ei - di
            if 0 <= pj < 3 and 0 <= pi < 3:
                if self.can_slide(pj, pi, ej, ei):
                    moves.append(((pj, pi), (ej, ei)))
        
        # Also check if ship can slide off board to goal_tile.
        ship_pos = None
        ship_id = None
        for tj in range(3):
            for ti in range(3):
                pid = self.board[tj, ti]
                if pid < 8 and self.setup.pieces[pid].is_ship:
                    ship_pos = (tj, ti)
                    ship_id = pid
                    break
        
        if ship_pos:
            tj, ti = ship_pos
            # goal_tile must be adjacent to ship_pos
            if abs(tj - goal_tile[0]) + abs(ti - goal_tile[1]) == 1:
                if self.can_slide(tj, ti, goal_tile[0], goal_tile[1]):
                    moves.append(((tj, ti), goal_tile))
        
        return moves

    def do_move(self, from_pos, to_pos):
        new_board = self.board.copy()
        fj, fi = from_pos
        tj, ti = to_pos
        piece_id = new_board[fj, fi]
        if 0 <= tj < 3 and 0 <= ti < 3:
            new_board[tj, ti] = piece_id
            new_board[fj, fi] = 8
        else:
            # Piece (ship) moved off board.
            new_board[fj, fi] = 8
        return BoardState(self.setup, new_board)

    def is_solved(self):
        # One way to check is if ship is no longer on board
        for tj in range(3):
            for ti in range(3):
                pid = self.board[tj, ti]
                if pid < 8 and self.setup.pieces[pid].is_ship:
                    return False
        return True

    def get_state_id(self):
        return tuple(self.board.flatten())