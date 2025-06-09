#!/bin/bash
#
# new-entry.sh ─ create a dated folder and LaTeX stub for a class diary
# ─────────────────────────────────────────────────────────────────────

# ─── 1. PROMPTS ─────────────────────────────────────────────────────
read -p "Enter the class name: " CLASS_NAME
read -p "Title:  " TITLE
read -p "Topic:  " TOPIC
read -p "Tags  (comma‑separated):  " TAGS

# ─── 2. DIRECTORIES ────────────────────────────────────────────────
BASE_DIR="/Users/jerichlee/Documents/jerich"
TARGET_DIR="$BASE_DIR/classes/$CLASS_NAME/diary"

[[ -d "$TARGET_DIR" ]] || { echo "Error: '$TARGET_DIR' not found." ; exit 1 ; }

# ─── 3. DATED FOLDER NAME (MM‑DD + duplicate suffix) ───────────────
DATE_MMDD=$(date +%m-%d)
FOLDER="$DATE_MMDD"
i=1
while [[ -d "$TARGET_DIR/$FOLDER" ]]; do
  FOLDER="$DATE_MMDD.$i"
  ((i++))
done
mkdir -p "$TARGET_DIR/$FOLDER"

# ─── 4. METADATA / FILE CREATION ───────────────────────────────────
DATE_ISO=$(date +%Y-%m-%d)
DATE_HUMAN=$(date +"%B %d, %Y")
FILE="$TARGET_DIR/$FOLDER/index.tex"

cat > "$FILE" <<EOF
% ------------------------------------------------------------
% title  : $TITLE
% topic  : $TOPIC
% tags   : $TAGS
% date   : $DATE_ISO
% ------------------------------------------------------------

\\documentclass[12pt]{article}

% Packages
\\usepackage[margin=1in]{geometry}
\\usepackage{amsmath,amssymb,amsthm}
\\usepackage{enumitem}
\\usepackage{hyperref}
\\usepackage{xcolor}
\\usepackage{import}
\\usepackage{xifthen}
\\usepackage{pdfpages}
\\usepackage{transparent}
\\usepackage{listings}
\\usepackage{tikz}
\\usepackage{physics}
\\usepackage{siunitx}
\\usepackage{booktabs}
\\usepackage{cancel}
\\usetikzlibrary{calc,patterns,arrows.meta,decorations.markings}

\\newcommand\\posttopic{$TOPIC}
\\newcommand\\posttags{$TAGS}
\\newcommand\\postdate{$DATE_ISO}

\\title{$TITLE}
\\author{Jerich Lee}
\\date{$DATE_HUMAN}

\\begin{document}
\\maketitle

% Your content starts here…

\\end{document}
EOF

echo "✔  Created '$FILE'"