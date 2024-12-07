#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# === Configuration ===

# Base directories
CLASSES_DIR="/Users/jerichlee/Documents/jerichlee.ai/classes"
BLOG_ENTRIES_DIR="/Users/jerichlee/Documents/jerichlee.ai/blog/entries"

# Paths to Python scripts
BLOG_PYTHON_SCRIPT="/Users/jerichlee/Documents/jerichlee.ai/tools/blog-latex-to-html.py"
DIARY_PYTHON_SCRIPT="/Users/jerichlee/Documents/jerichlee.ai/tools/math-tex-to-html.py"

# Path to the CSS file
CSS_PATH="/Users/jerichlee/Documents/jerichlee.ai/blog/style.css"

# Log file
LOG_FILE="/Users/jerichlee/Documents/jerichlee.ai/script.log"

# === Functions ===

# Function to log messages with timestamps
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to process all .tex files in a given directory recursively
process_all_tex_files() {
    local BASE_DIR="$1"
    local PYTHON_SCRIPT="$2"

    log "Starting processing of .tex files in '$BASE_DIR' with script '$PYTHON_SCRIPT'."

    if [ ! -d "$BASE_DIR" ]; then
        log "Error: Base directory '$BASE_DIR' does not exist!"
        return 1
    fi

    # Find all .tex files recursively
    find "$BASE_DIR" -type f -name "*.tex" | while read -r LATEX_FILE; do
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
        fi
    done

    log "Completed processing of .tex files in '$BASE_DIR'."
}

# Function to replace content between markers in index.html using perl
replace_between_markers_perl() {
    local marker="$1"        # e.g., HW_LINKS
    local replacement="$2"   # generated HTML links
    local file="$3"

    # Define start and end markers
    local start_marker="<!-- ${marker}_START -->"
    local end_marker="<!-- ${marker}_END -->"

    # Escape forward slashes and backslashes in the replacement string
    local replacement_escaped=$(echo -e "$replacement" | perl -pe 's/[\/\\]/\\$&/g')

    # Use perl to replace content between start and end markers
    perl -i.bak -0777 -pe "
        s/($start_marker)(.*?)($end_marker)/\$1\n$replacement_escaped\n\$3/s
    " "$file"
}

# Function to update the HW and Diary sections in index.html
update_index_html() {
    local COURSE_PATH="$1"
    local INDEX_FILE="$COURSE_PATH/index.html"

    log "Updating index.html for course at '$COURSE_PATH'."

    if [[ -f "$INDEX_FILE" ]]; then
        # Initialize variables to store HTML links
        local HW_LINKS=""
        local DIARY_LINKS=""

        # Calculate relative path from CLASSES_DIR to COURSE_PATH
        local relative_course_path="${COURSE_PATH#$CLASSES_DIR/}"  # e.g., "fall-2024/tam-470"

        log "Relative course path: '$relative_course_path'"

        # Process hw folders
        local HW_BASE_PATH="$COURSE_PATH/hw"
        if [[ -d "$HW_BASE_PATH" ]]; then
            log "Processing HW directories in '$HW_BASE_PATH'"

            for HW_DIR in "$HW_BASE_PATH"/*/; do
                if [[ -d "$HW_DIR" ]]; then
                    local HW_NAME=$(basename "$HW_DIR")
                    local HW_INDEX_FILE="${HW_DIR}index.html"

                    if [[ -f "$HW_INDEX_FILE" ]]; then
                        local HW_LINK="/Users/jerichlee/Documents/jerichlee.ai/classes/$relative_course_path/hw/$HW_NAME/index.html"
                        HW_LINKS+="<li><a href=\"$HW_LINK\">$HW_NAME</a></li>\n"
                        log "Added HW link: '$HW_LINK'"
                    else
                        log "Warning: 'index.html' not found in '$HW_DIR'. Skipping..."
                    fi
                else
                    log "Warning: '$HW_DIR' is not a directory. Skipping..."
                fi
            done
        else
            log "No HW directory found at '$HW_BASE_PATH' for course '$COURSE_PATH'."
        fi

        # Process diary folders
        local DIARY_BASE_PATH="$COURSE_PATH/diary"
        if [[ -d "$DIARY_BASE_PATH" ]]; then
            log "Processing Diary directories in '$DIARY_BASE_PATH'"

            for DIARY_DIR in "$DIARY_BASE_PATH"/*/; do
                if [[ -d "$DIARY_DIR" ]]; then
                    local DIARY_NAME=$(basename "$DIARY_DIR")
                    local DIARY_INDEX_FILE="${DIARY_DIR}index.html"

                    if [[ -f "$DIARY_INDEX_FILE" ]]; then
                        local DIARY_LINK="/Users/jerichlee/Documents/jerichlee.ai/classes/$relative_course_path/diary/$DIARY_NAME/index.html"
                        DIARY_LINKS+="<li><a href=\"$DIARY_LINK\">$DIARY_NAME</a></li>\n"
                        log "Added Diary link: '$DIARY_LINK'"
                    else
                        log "Warning: 'index.html' not found in '$DIARY_DIR'. Skipping..."
                    fi
                else
                    log "Warning: '$DIARY_DIR' is not a directory. Skipping..."
                fi
            done
        else
            log "No Diary directory found at '$DIARY_BASE_PATH' for course '$COURSE_PATH'."
        fi

        # Backup the existing index.html
        cp "$INDEX_FILE" "$INDEX_FILE.bak"
        log "Backup created for index.html at '$INDEX_FILE.bak'."

        # Replace the HW_LINKS section
        if [[ -n "$HW_LINKS" ]]; then
            HW_LINKS=$(printf "$HW_LINKS")
            replace_between_markers_perl "HW_LINKS" "$HW_LINKS" "$INDEX_FILE"
            log "Updated HW_LINKS in '$INDEX_FILE'."
        else
            log "No HW links to update in '$INDEX_FILE'."
        fi

        # Replace the DIARY_LINKS section
        if [[ -n "$DIARY_LINKS" ]]; then
            DIARY_LINKS=$(printf "$DIARY_LINKS")
            replace_between_markers_perl "DIARY_LINKS" "$DIARY_LINKS" "$INDEX_FILE"
            log "Updated DIARY_LINKS in '$INDEX_FILE'."
        else
            log "No Diary links to update in '$INDEX_FILE'."
        fi

        log "index.html updated for course at '$COURSE_PATH'."
    else
        log "index.html not found in '$COURSE_PATH'. Skipping..."
    fi
}

# Function to update index.html for all courses
update_all_index_html() {
    local BASE_CLASSES_DIR="$1"

    log "Starting update of index.html files in all course directories under '$BASE_CLASSES_DIR'."

    # Iterate over each semester folder
    for SEMESTER in "$BASE_CLASSES_DIR"/*; do
        if [[ -d "$SEMESTER" ]]; then
            local SEMESTER_NAME=$(basename "$SEMESTER")
            log "Processing semester: $SEMESTER_NAME"
            # Iterate over each course folder within the semester
            for COURSE in "$SEMESTER"/*; do
                if [[ -d "$COURSE" ]]; then
                    update_index_html "$COURSE"
                fi
            done
        else
            log "Skipping non-directory item: $SEMESTER"
        fi
    done

    log "Completed updating index.html files in '$BASE_CLASSES_DIR'."
}

# === Main Execution ===

log "===== Script Started ====="

# Step 1: Process .tex files in 'classes' directory using the diary Python script
process_all_tex_files "$CLASSES_DIR" "$DIARY_PYTHON_SCRIPT"

# Step 2: Update index.html files for all courses in 'classes' directory
update_all_index_html "$CLASSES_DIR"

# Step 3: Process .tex files in 'blog/entries' directory using the blog Python script
process_all_tex_files "$BLOG_ENTRIES_DIR" "$BLOG_PYTHON_SCRIPT"

log "===== Script Completed ====="