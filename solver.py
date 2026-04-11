import collections
from board_io import parse_board
from board import BoardState

def solve(initial_state: BoardState, goal_tile=(3, 1)):
    if initial_state.is_solved():
        return []

    # Queue stores (state, path)
    queue = collections.deque([(initial_state, [])])
    visited = {initial_state.get_state_id()}

    while queue:
        curr_state, path = queue.popleft()

        for from_pos, to_pos in curr_state.get_possible_moves(goal_tile):
            next_state = curr_state.do_move(from_pos, to_pos)
            
            new_path = path + [(from_pos, to_pos)]
            if next_state.is_solved():
                return new_path
            
            state_id = next_state.get_state_id()
            if state_id not in visited:
                visited.add(state_id)
                queue.append((next_state, new_path))
    
    return None

def main():
    import sys
    question_num = sys.argv[1] if len(sys.argv) > 1 else "01"
    
    try:
        initial_state = parse_board(question_num)
    except FileNotFoundError:
        print(f"Question {question_num} not found.")
        return

    solution = solve(initial_state, (3, 1))

    if solution is None:
        print("No solution found.")
    else:
        res = []
        for (f, t) in solution:
            # Empty spot movement direction (t -> f)
            dj = f[0] - t[0]
            di = f[1] - t[1]
            if dj == 1: res.append("D")
            elif dj == -1: res.append("U")
            elif di == 1: res.append("R")
            elif di == -1: res.append("L")
        print("".join(res))

if __name__ == "__main__":
    main()
