#!/bin/bash

# Define paths
downloads_dir="/Users/jerichlee/Downloads"
pdfs_dir="/Users/jerichlee/Documents/jerich.ai/classes/fall-2024/math-447/lecture-slides/Lecture-Slides-Pdfs"
html_dir="/Users/jerichlee/Documents/jerich.ai/classes/fall-2024/math-447/lecture-slides/"
index_file="/Users/jerichlee/Documents/jerich.ai/classes/fall-2024/math-447/index.html"

# Find the lectureX.pdf file with the largest X in the Downloads folder
latest_lecture=$(ls ${downloads_dir}/lecture*.pdf | grep -o 'lecture[0-9]\+' | grep -o '[0-9]\+' | sort -n | tail -1)

if [ -z "$latest_lecture" ]; then
    echo "No lectureX.pdf files found in $downloads_dir"
    exit 1
fi

# Define the full file name with 'lectureX.pdf'
latest_pdf="lecture${latest_lecture}.pdf"

# Copy the latest lecture PDF to the target directory
cp "${downloads_dir}/${latest_pdf}" "${pdfs_dir}/"

# Generate the HTML file content
html_content='<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lecture '"${latest_lecture}"' - MATH 447: Real Variables</title>
    <link rel="stylesheet" href="../../css/styles.css">
    <style>
        .nav-buttons {
            position: fixed;
            bottom: 20px;
            right: 20px;
        }
        .nav-buttons a {
            display: inline-block;
            padding: 10px 20px;
            margin-left: 10px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
        .nav-buttons a:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <nav>
        <a href="../index.html">Back to Course Contents</a>
    </nav>

    <h1>Lecture '"${latest_lecture}"'</h1>

    <iframe src="lecture-slides-pdfs/lecture'"${latest_lecture}"'.pdf" width="100%" height="600px"></iframe>

    <div class="nav-buttons">
        <a href="lecture-'"$((${latest_lecture}-1))"'.html" class="back">Back</a>
        <a href="lecture-'"$((${latest_lecture}+1))"'.html" class="next">Next</a>
    </div>

    <script src="../../js/script.js"></script>
</body>
</html>'

# Write the HTML content to a new file
html_file="${html_dir}/lecture-${latest_lecture}.html"
echo "$html_content" > "$html_file"

# Prepare the new lecture entry for index.html
lecture_entry="                        <li><a href=\"lecture-slides/lecture-${latest_lecture}.html\">Lecture ${latest_lecture}</a></li>"

# Use awk to find the Lecture Slides section and append the new lecture
awk -v entry="$lecture_entry" '
/<li>Lecture Slides/ {found = 1}
found && /<\/ul>/ {print entry; found = 0}
{print}
' "$index_file" > temp_index.html && mv temp_index.html "$index_file"

echo "Copied ${latest_pdf} to ${pdfs_dir}, created ${html_file}, and appended the lecture to ${index_file}."