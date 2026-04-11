# Asteroid Escape Solver

A comprehensive toolset for solving, visualizing, and creating levels for the "Asteroid Escape" puzzle game. This project implements the game logic, a BFS-based shortest-path solver, a Pygame-based visualizer and level editor, and tools for exporting solutions as animated WebP files.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Solving and Visualizing](#solving-and-visualizing)
- [Level Editor](#level-editor)
- [Batch Exporting Solutions](#batch-exporting-solutions)
- [Project Structure](#project-structure)
- [Testing](#testing)

## Prerequisites
- Python 3.8+
- Pygame (or Pygame-ce)
- NumPy
- Pillow (for WebP export)
- tqdm (for batch export progress)

## Installation
1. Clone this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Solving and Visualizing

### `solver_ui.py`
The primary entry point to solve a level and visualize the solution.

**Usage:**
```bash
python3 solver_ui.py [problem_id] [flags]
```

**Arguments:**
- `problem_id`: (Optional) The ID of the level to solve (e.g., `01`, `12`). Defaults to `01`.

**Flags:**
- `--autoplay`: Automatically starts animating the solution when the visualizer opens.
- `--no-controls`: Hides the keyboard control instructions in the UI.

### `solver.py`
Can also be run directly for a CLI-only solution output (no GUI).

**Usage:**
```bash
python3 solver.py [problem_id]
```

## Level Editor

### `level_editor.py`
An interactive GUI for creating or modifying levels.

**Usage:**
```bash
python3 level_editor.py [problem_id]
```

**Controls:**
- **Left Click (Sidebar):** Select a piece to place.
- **Left Click (Board):** Drag an already-placed piece.
- **Right Click (Board):** Remove a piece from the board.
- **'R' Key (while dragging):** Rotate the selected piece.
- **'S' Key:** Save the current layout to `questions/[problem_id].txt`.
- **'ESC':** Quit without saving.

### `edit_and_solve.sh`
A convenience script that opens the level editor and, upon saving, immediately runs the solver with autoplay.

**Usage:**
```bash
./edit_and_solve.sh [problem_id]
```

## Batch Exporting Solutions

### `batch_export.py`
Solves multiple levels and exports their solutions as animated WebP files in the `solutions/` folder.

**Usage:**
```bash
python3 batch_export.py [flags]
```

**Flags:**
- `-p`, `--parallelism`: Number of parallel export processes (default: 10).

### `export_webp.py`
Exports a single level's solution to WebP.

**Usage:**
```bash
python3 export_webp.py [problem_id]
```

## Project Structure
- `board.py`: Core game logic, piece definitions, and collision detection.
- `board_io.py`: Parsers for the ASCII level format and board occupancy debugging.
- `solver.py`: BFS search algorithm to find the shortest path.
- `visualizer.py`: Pygame rendering logic for the board and animations.
- `questions/`: Directory containing 60 pre-defined puzzle levels (`01.txt` to `60.txt`).
- `solutions/`: Directory where exported WebP solutions are stored.
- `test/`: Contains reference files for regression testing.

## Testing
To run the basic I/O and occupancy tests:
```bash
python3 test_board_io.py
```
