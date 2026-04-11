import collections
import time
from board import BoardState

def solve(initial_state: BoardState, goal_tile=(3, 1)):
    start_time = time.time()
    
    if initial_state.is_solved():
        return [], 0, 0.0

    # Queue stores (state, path)
    queue = collections.deque([(initial_state, [])])
    visited = {initial_state.get_state_id()}

    while queue:
        curr_state, path = queue.popleft()

        for from_pos, to_pos in curr_state.get_possible_moves(goal_tile):
            next_state = curr_state.do_move(from_pos, to_pos)
            
            new_path = path + [(from_pos, to_pos)]
            if next_state.is_solved():
                end_time = time.time()
                return new_path, len(visited), end_time - start_time
            
            state_id = next_state.get_state_id()
            if state_id not in visited:
                visited.add(state_id)
                queue.append((next_state, new_path))
    
    end_time = time.time()
    return None, len(visited), end_time - start_time

def main():
    import sys
    import json
    from board_io import parse_board, parse_board_content
    
    arg = sys.argv[1] if len(sys.argv) > 1 else "01"
    
    try:
        if arg == "-":
            content = sys.stdin.read()
            initial_state = parse_board_content(content)
        else:
            initial_state = parse_board(arg)
    except Exception as e:
        print(f"Error loading board: {e}")
        return

    solution, visited_count, duration = solve(initial_state, (3, 1))

    if solution is None:
        print(json.dumps({"error": "No solution found"}))
    else:
        # Machine-readable output for the full solution
        res = []
        for (f, t) in solution:
            res.append({"from": list(f), "to": list(t)})
        print(json.dumps(res))
        
        # Human-readable info for debugging
        # print(f"Found solution in {len(solution)} moves.", file=sys.stderr)
        # print(f"States visited: {visited_count}", file=sys.stderr)
        # print(f"Search time: {duration:.4f}s", file=sys.stderr)

if __name__ == "__main__":
    main()
