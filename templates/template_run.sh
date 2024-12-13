#!/bin/bash

# -------------------------------------------------------------------
# Script Name: run.sh
# Description: Takes two Python script files as arguments and starts them.
# Usage: ./run.sh path/to/script1.py path/to/script2.py
# -------------------------------------------------------------------

# Exit immediately if a command exits with a non-zero status
set -e

# Function to display usage information
usage() {
    echo "Usage: $0 path/to/script1.py path/to/script2.py"
    echo "Example: $0 ./script1.py ./script2.py"
    exit 1
}

# Check if exactly two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Error: Exactly two arguments are required."
    usage
fi

# Assign arguments to variables
SCRIPT1="$1"
SCRIPT2="$2"

# Function to check if a file exists and is a Python script
check_script() {
    local script="$1"
    if [ ! -f "$script" ]; then
        echo "Error: File '$script' does not exist."
        exit 1
    fi
    if [[ "$script" != *.py ]]; then
        echo "Warning: File '$script' does not have a .py extension."
    fi
}

# Check both scripts
check_script "$SCRIPT1"
check_script "$SCRIPT2"

# Determine which python command to use
# Prefer 'python3' if available
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Error: Python is not installed or not in PATH."
    exit 1
fi

echo "Using Python interpreter: $PYTHON_CMD"

# Define log file names based on script names
SCRIPT1_LOG="$(basename "$SCRIPT1" .py).log"
SCRIPT2_LOG="$(basename "$SCRIPT2" .py).log"

# Start the first Python script in the background and redirect output
echo "Starting '$SCRIPT1'..."
$PYTHON_CMD "$SCRIPT1" > "$SCRIPT1_LOG" 2>&1 &
PID1=$!
echo "'$SCRIPT1' started with PID $PID1. Output redirected to '$SCRIPT1_LOG'."

# Start the second Python script in the background and redirect output
echo "Starting '$SCRIPT2'..."
$PYTHON_CMD "$SCRIPT2" > "$SCRIPT2_LOG" 2>&1 &
PID2=$!
echo "'$SCRIPT2' started with PID $PID2. Output redirected to '$SCRIPT2_LOG'."

# Wait for both scripts to finish
echo "Waiting for both Python scripts to finish..."
wait $PID1
STATUS1=$?
if [ $STATUS1 -ne 0 ]; then
    echo "Error: '$SCRIPT1' exited with status $STATUS1."
else
    echo "'$SCRIPT1' completed successfully."
fi

wait $PID2
STATUS2=$?
if [ $STATUS2 -ne 0 ]; then
    echo "Error: '$SCRIPT2' exited with status $STATUS2."
else
    echo "'$SCRIPT2' completed successfully."
fi

echo "Both Python scripts have completed."
