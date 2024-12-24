#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# === Configuration ===

# Base directories
CLASSES_DIR="/Users/jerichlee/Documents/jerich/classes"
BLOG_ENTRIES_DIR="/Users/jerichlee/Documents/jerich/blog/entries"

# Paths to Python scripts
BLOG_PYTHON_SCRIPT="/Users/jerichlee/Documents/jerich/scripts/blog-latex-to-html.py"
DIARY_PYTHON_SCRIPT="/Users/jerichlee/Documents/jerich/scripts/math-tex-to-html.py"

# Path to the CSS file
CSS_PATH="https://jerichlee2.github.io/Jerich.ai/style2.css"

# Log file
LOG_FILE="/Users/jerichlee/Documents/jerichlee.ai/script.log"

# === Functions ===

# Function to log messages with timestamps
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# === Main Execution ===

# Check that exactly one argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 path_to_tex_file"
    exit 1
fi

LATEX_FILE="$1"

# Check if the file exists
if [ ! -f "$LATEX_FILE" ]; then
    echo "Error: Specified file '$LATEX_FILE' does not exist!"
    exit 1
fi

# Check that it is a .tex file
if [[ $LATEX_FILE != *.tex ]]; then
    echo "Error: '$LATEX_FILE' does not end with '.tex'"
    exit 1
fi

log "===== Script Started ====="

# Determine which Python script to use (if needed)
if [[ "$LATEX_FILE" == $CLASSES_DIR* ]]; then
    PYTHON_SCRIPT="$DIARY_PYTHON_SCRIPT"
elif [[ "$LATEX_FILE" == $BLOG_ENTRIES_DIR* ]]; then
    PYTHON_SCRIPT="$BLOG_PYTHON_SCRIPT"
else
    # Default to DIARY_PYTHON_SCRIPT if not in either directory
    PYTHON_SCRIPT="$DIARY_PYTHON_SCRIPT"
fi

# Define the output HTML file path
OUTPUT_HTML="${LATEX_FILE%.tex}.html"

log "Converting LaTeX file: $LATEX_FILE"
log "Output HTML file: $OUTPUT_HTML"

# Invoke the Python program
python3 "$PYTHON_SCRIPT" "$LATEX_FILE" "$OUTPUT_HTML" "$CSS_PATH"

# Check if the Python script ran successfully
if [ $? -eq 0 ]; then
    log "HTML conversion successful for file: $LATEX_FILE"
else
    log "HTML conversion failed for file: $LATEX_FILE"
    exit 1
fi

log "===== Script Completed ====="