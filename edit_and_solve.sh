#!/bin/bash

# Check if question number is provided
if [ -z "$1" ]; then
    echo "Usage: ./edit_and_solve.sh <question_number>"
    exit 1
fi

# Run the editor, and if it exits successfully (e.g. via SAVE), run the solver with autoplay
python3 level_editor.py "$1" && python3 solver_main.py "$1" --autoplay
