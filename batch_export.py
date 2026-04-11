import os
import sys
import subprocess
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def export_single(q_id):
    """Worker function to export a single question."""
    try:
        subprocess.run(
            [sys.executable, "export_webp.py", q_id],
            capture_output=True,
            text=True,
            check=True
        )
        return q_id, True, None
    except subprocess.CalledProcessError as e:
        return q_id, False, e.stderr

def batch_export():
    parser = argparse.ArgumentParser(description="Batch export solutions to WebP.")
    parser.add_argument("-p", "--parallelism", type=int, default=10, help="Number of parallel exports (default: 10)")
    args = parser.parse_args()

    questions_dir = "questions"
    solutions_dir = "solutions"
    
    if not os.path.exists(questions_dir):
        print(f"Error: {questions_dir} folder not found.")
        return

    os.makedirs(solutions_dir, exist_ok=True)

    questions = [f[:-4] for f in os.listdir(questions_dir) if f.endswith(".txt")]
    existing_solutions = [f[:-5] for f in os.listdir(solutions_dir) if f.endswith(".webp")]
    
    to_export = [q for q in questions if q not in existing_solutions]
    to_export.sort()

    if not to_export:
        print("All solutions are already exported.")
        return

    print(f"Found {len(to_export)} missing solutions. Starting batch export with parallelism={args.parallelism}...")

    # Use ThreadPoolExecutor to manage subprocesses in parallel
    with ThreadPoolExecutor(max_workers=args.parallelism) as executor:
        futures = {executor.submit(export_single, q_id): q_id for q_id in to_export}
        
        # Use tqdm to track progress as tasks complete
        for future in tqdm(as_completed(futures), total=len(futures), desc="Exporting WebPs", unit="file"):
            q_id, success, error_msg = future.result()
            if not success:
                print(f"\nError exporting {q_id}:")
                print(error_msg)

    print("\nBatch export complete.")

if __name__ == "__main__":
    batch_export()
