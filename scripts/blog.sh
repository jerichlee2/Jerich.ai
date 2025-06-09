#!/bin/bash

# Prompt the user for the class name
read -p "Enter the class name (or type 'blog' for blog entries): " CLASS_NAME

# Define the base directory
BASE_DIR="/Users/jerichlee/Documents/jerich"

# Adjust target directory based on the input
if [[ "$CLASS_NAME" == "blog" ]]; then
    TARGET_DIR="$BASE_DIR/blog/entries"
else
    TARGET_DIR="$BASE_DIR/classes/$CLASS_NAME/diary"
fi

# Ensure the target directory exists
if [[ ! -d "$TARGET_DIR" ]]; then
    echo "Error: Target directory '$TARGET_DIR' does not exist!"
    exit 1
fi

# Get the current date in MM-DD format
DATE=$(date +%m-%d)

# Check if the folder already exists and handle duplicates
FOLDER_NAME="$DATE"
SUFFIX=1
while [[ -d "$TARGET_DIR/$FOLDER_NAME" ]]; do
    FOLDER_NAME="$DATE.$SUFFIX"
    ((SUFFIX++))
done

# Create the full path for the new folder
FULL_PATH="$TARGET_DIR/$FOLDER_NAME"
mkdir -p "$FULL_PATH"

# Get the full current date (e.g., November 25, 2024)
FULL_DATE=$(date +"%B %d, %Y")

# Create the LaTeX file
FILE_PATH="$FULL_PATH/index.tex"
cat <<EOL > "$FILE_PATH"
\documentclass[12pt]{article}

% Packages
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{import}
\usepackage{xifthen}
\usepackage{pdfpages}
\usepackage{transparent}
\usepackage{listings}
\usepackage{tikz}
\usepackage{physics}
\usepackage{siunitx}
\usepackage{booktabs}
\usepackage{cancel}
  \usetikzlibrary{calc,patterns,arrows.meta,decorations.markings}


\DeclareMathOperator{\Log}{Log}
\DeclareMathOperator{\Arg}{Arg}

\lstset{
    breaklines=true,         % Enable line wrapping
    breakatwhitespace=false, % Wrap lines even if there's no whitespace
    basicstyle=\ttfamily,    % Use monospaced font
    frame=single,            % Add a frame around the code
    columns=fullflexible,    % Better handling of variable-width fonts
}

\newcommand{\incfig}[1]{%
    \def\svgwidth{\columnwidth}
    \import{./Figures/}{#1.pdf_tex}
}
\theoremstyle{definition} % This style uses normal (non-italicized) text
\newtheorem{solution}{Solution}
\newtheorem{proposition}{Proposition}
\newtheorem{problem}{Problem}
\newtheorem{lemma}{Lemma}
\newtheorem{theorem}{Theorem}
\newtheorem{remark}{Remark}
\newtheorem{note}{Note}
\newtheorem{definition}{Definition}
\newtheorem{example}{Example}
\newtheorem{corollary}{Corollary}
\theoremstyle{plain} % Restore the default style for other theorem environments
%

% Theorem-like environments
% Title information
\title{}
\author{Jerich Lee}
\date{\today}

\begin{document}

\maketitle

\end{document}
EOL

# Output success message
echo "Folder '$FOLDER_NAME' and file 'index.tex' created successfully at $FULL_PATH."