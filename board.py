import numpy as np
from typing import List

# A location on the board.
class Loc:
    def __init__(self, y, x):
        self.y = y
        self.x = x

    # rotate 90 degrees.
    def rotate(self) -> "Loc":
        return Loc(-self.x, self.y)


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
        # rotate the repr
        repr_str = self.repr_str[1:4] + self.repr_str[0:1]
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
    piece = Piece(5, [Loc(-1, -1), Loc(-1, 1), Loc(-2, -1), Loc(-2,1)], 0, "AA  ")
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
        # each number corresponds to setup.piece[i], or 9 for the empty space
        self.board = board
        # Check that board is valid.
        assert self.board.shape == (3,3)
        all_values = sorted(self.board.flatten().tolist())
        for i in range(9):
            assert all_values[i] == i


    def get_state_id(): # for DPS tracing purpose
        # todo: just 
        pass