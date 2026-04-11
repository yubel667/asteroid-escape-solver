import sys
from board_io import parse_board
from solver import solve
from visualizer import run_visualizer

def main():
    question_num = sys.argv[1] if len(sys.argv) > 1 else "01"
    
    try:
        print(f"Loading challenge {question_num}...")
        initial_state = parse_board(question_num)
    except FileNotFoundError:
        print(f"Error: Question {question_num} not found in questions/ folder.")
        return
    except Exception as e:
        print(f"Error parsing board: {e}")
        return

    print("Searching for shortest solution...")
    solution = solve(initial_state)

    if solution is None:
        print("No solution found for this challenge.")
        # Open UI anyway to show the initial state
        run_visualizer(initial_state, None)
    else:
        print(f"Found solution in {len(solution)} moves.")
        print("Opening visualizer...")
        run_visualizer(initial_state, solution)

if __name__ == "__main__":
    main()
