#!/bin/bash

# Check if a folder name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <folder-name>"
  exit 1
fi

# Input parameter
FOLDER_NAME="$1"

# Base path where the folder will be created
BASE_PATH="/Users/jerichlee/Documents/jerich/classes"

# Full path to the new folder
FULL_PATH="$BASE_PATH/$FOLDER_NAME"

# Create the folder structure
mkdir -p "$FULL_PATH/assets"
mkdir -p "$FULL_PATH/diary"
mkdir -p "$FULL_PATH/hw"
mkdir -p "$FULL_PATH/lecture-slides"
mkdir -p "$FULL_PATH/resources"

# Define the path for index.html
INDEX_FILE="$FULL_PATH/index.html"

# Create the index.html file with the provided template
cat > "$INDEX_FILE" <<EOL
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$FOLDER_NAME</title>
    <link rel="stylesheet" href="https://jerichlee2.github.io/Jerich.ai/style.css">

    <script>
        MathJax = {
            tex: {
                inlineMath: [['\$', '\$'], ['\\\\(', '\\\\)']]
            },
            svg: {
                fontCache: 'global'
            }
        };
    </script>
    <script type="text/javascript" id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js">
    </script>
</head>
<body>
    <!-- Header Section -->
    <div id="dhead" class="container">
        <div class="row">
            <div id="ddesc">
                <h1>$FOLDER_NAME</h1>
                <h2>University of Illinois at Urbana-Champaign</h2>
                <nav>
                    <a href="https://jerichlee2.github.io/Jerich.ai/index.html">Home</a>
                </nav>
            </div>
        </div>
    </div>

    <hr>

    <div class="container">
        <div style="background-color: #eee; padding: 20px; margin-top: 20px;">
            <!-- Course Contents Section -->
            <div class="content">
                <h1>Course Contents:</h1>
                <ul>
                    <!-- DIARY_LINKS -->
                </ul>
            </div>
        </div>

        <hr>
        <div style="background-color: #eee; padding: 20px; margin-top: 20px;">
             <div class="container">
                <div class="ctitle">HW</div>
                <ul>
                    <!-- HW_LINKS -->
                </ul>
            </div>
        </div>
        <div style="background-color: #eee; padding: 20px; margin-top: 20px;">
            <div class="container">
                <div class="ctitle">Lectures</div>
                <ul>
                </ul>
            </div>
        </div>
        <div style="background-color: #eee; padding: 20px; margin-top: 20px;">
            <div class="container">
                <div class="ctitle">Resources</div>
                <ul>
                </ul>
            </div>
        </div>
        <div style="background-color: #eee; padding: 20px; margin-top: 20px;">
            <div class="container">
                <div class="ctitle">Exam Prep</div>
                <ul>
                </ul>
            </div>
        </div> 

        <br><br><br><br><br>

        <!-- Scripts -->
        <script src="../js/script.js"></script>
    </body>
</html>
EOL

echo "Folder structure created with index.html for '$FOLDER_NAME' at '$FULL_PATH'."