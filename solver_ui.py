import sys
import argparse
from board_io import parse_board
from solver import solve
from visualizer import run_visualizer

def main():
    parser = argparse.ArgumentParser(description="Asteroid Escape Solver")
    parser.add_argument("problem_id", nargs="?", default="01", help="ID of the level to solve (e.g. 01)")
    parser.add_argument("--autoplay", action="store_true", help="Start the visualizer in auto-play mode")
    parser.add_argument("--no-controls", action="store_false", dest="show_controls", help="Hide helper control text in UI")
    parser.set_defaults(show_controls=True)
    
    args = parser.parse_args()
    question_num = args.problem_id
    
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
    solution, visited_count, duration = solve(initial_state)

    if solution is None:
        print(f"No solution found for this challenge. (Visited {visited_count} states in {duration:.4f}s)")
        run_visualizer(initial_state, None, autoplay=False, show_controls=args.show_controls, level_id=question_num)
    else:
        print(f"Found solution in {len(solution)} moves.")
        print(f"States visited: {visited_count}")
        print(f"Search time: {duration:.4f}s")
        print("Opening visualizer...")
        run_visualizer(initial_state, solution, autoplay=args.autoplay, show_controls=args.show_controls, level_id=question_num)

if __name__ == "__main__":
    main()
