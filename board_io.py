
# Parsers & visualizers for the board.
import numpy as np
from board import BoardState, BoardSetup, PIECES

def parse_board(question_number: str) -> BoardState:
    with open(f"questions/{question_number}.txt", "r") as f:
        lines = f.read().splitlines()
    if len(lines) != 10:
        raise ValueError("parsing fails")
    # preprocess: parse into a 6x6 string array
    for row, line in enumerate(lines):
        if len(line) != 10:
            print(row, line, len(line))
            raise ValueError("parsing fails")
        if row in [0,3,6,9]:
            if lines[row] != "+--+--+--+":
                raise ValueError("parsing fails")
            continue
        for col, char in enumerate(line):
            if col in [0,3,6,9] and char != '|':
                raise ValueError("parsing fails")

    buffer = []
    for _ in range(6):
        line_buffer = [None for _ in range(6)]
        buffer.append(line_buffer)
    useful_indices = [1,2,4,5,7,8]
    for j, row in enumerate(useful_indices):
        for i, col in enumerate(useful_indices):
            buffer[j][i] = lines[row][col]

    pieces_used = []
    board = np.full((3,3), 8, dtype=np.int8)
    for tile_j in range(3):
        for tile_i in range(3):
            # read repr
            # 12
            # 43
            repr_str = buffer[tile_j*2][tile_i*2]
            repr_str += buffer[tile_j*2][tile_i*2+1]
            repr_str += buffer[tile_j*2+1][tile_i*2+1]
            repr_str += buffer[tile_j*2+1][tile_i*2]
            if repr_str == "    ":
                # empty space
                continue
            for piece in PIECES: # low efficieny, but fine for parsing.
                if piece.repr_str == repr_str:
                    board[tile_j][tile_i] = len(pieces_used)
                    pieces_used.append(piece)
                    break
            else:
                print([piece.repr_str for piece in PIECES])
                raise ValueError(f"Invalid repr string {repr_str}")
    board_setup = BoardSetup(pieces_used)
    return BoardState(board_setup, board)

EMPTY_BUFFER = """+--+--+--+
|  |  |  |
|  |  |  |
+--+--+--+
|  |  |  |
|  |  |  |
+--+--+--+
|  |  |  |
|  |  |  |
+--+--+--+"""

def serialize_board(board_state: BoardState):
    # serialize back to initial ascii format.
    lines = EMPTY_BUFFER.splitlines()
    buffer = []
    for line in lines:
        buffer.append([c for c in line])
    for tile_j in range(3):
        for tile_i in range(3):
            piece_id = board_state.board[tile_j][tile_i]
            if piece_id == 8:
                # skip empty board
                continue
            offset_j = tile_j * 3 + 1
            offset_i = tile_i * 3 + 1
            repr_str = board_state.setup.pieces[piece_id].repr_str
            buffer[offset_j][offset_i] = repr_str[0]
            buffer[offset_j][offset_i+1] = repr_str[1]
            buffer[offset_j+1][offset_i+1] = repr_str[2]
            buffer[offset_j+1][offset_i] = repr_str[3]
    return "\n".join("".join(l) for l in buffer)

def debug_occupancy_map(board_state: BoardState):
    # we use a 11x11 board to track every occupancy
    # to handle out of boundary ones. each tile contains 3 tiles
    # and may overflow.
    board = []
    for _ in range(11):
        board.append([' ' for _ in range(11)])
    for tile_j in range(3):
        for tile_i in range(3):
            if board_state.board[tile_j][tile_i] == 8:
                # skip empty piece
                continue
            center_j = 2 + tile_j * 3
            center_i = 2 + tile_i * 3
            piece = board_state.setup.pieces[board_state.board[tile_j][tile_i]]
            for cell in piece.cells:
                y = center_j + cell.y
                x = center_i + cell.x
                char = piece.repr_char
                if board[y][x] == ' ':
                    board[y][x] = char
                else:
                    board[y][x] = '?' # error state
    # interleave with boundaries

    return "\n".join("".join(l) for l in board)