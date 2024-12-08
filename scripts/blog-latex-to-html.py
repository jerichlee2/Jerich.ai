import os
import re
import sys
from datetime import datetime

def latex_to_html(latex_file, output_html, css_path):
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Converted Document</title>
    <link rel="stylesheet" href="{css_path}">
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script>
        MathJax = {{
            tex: {{
                inlineMath: [['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$']],
                packages: {{ '[+]': ['ams'] }},
                processEscapes: true
            }},
            options: {{
                skipHtmlTags: ['noscript', 'style', 'textarea', 'pre', 'code']
            }}
        }};
    </script>
    <script id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
    </script>
    <style>
        p {{
            text-indent: 20px;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    <a href="/Users/jerichlee/Documents/jerichlee.ai/blog/index.html" class="home-button">Back</a>
    <div id="main">
        CONTENT_PLACEHOLDER
    </div>
</body>
</html>
    """.format(css_path=css_path)

    try:
        with open(latex_file, 'r') as file:
            latex_content = file.read()

        # Current date
        current_date = datetime.now().strftime("%B %d, %Y")

        # Extract preamble information for title, author, and date
        title_match = re.search(r"\\title\{(.*?)\}", latex_content, re.DOTALL)
        author_match = re.search(r"\\author\{(.*?)\}", latex_content, re.DOTALL)
        date_match = re.search(r"\\date\{(.*?)\}", latex_content, re.DOTALL)

        title = f"<h1>{title_match.group(1).strip()}</h1>" if title_match else ""
        author = f"<h3>{author_match.group(1).strip()}</h3>" if author_match else ""

        if date_match:
            date_content = date_match.group(1).replace("\\today", current_date).strip()
            date = f"<h4>{date_content}</h4>"
        else:
            date = ""

        title_block = f"{title}\n{author}\n{date}"

        start = latex_content.find("\\begin{document}")
        end = latex_content.find("\\end{document}")

        if start == -1 or end == -1:
            raise ValueError("Could not find \\begin{document} or \\end{document} in the LaTeX file.")

        start += len("\\begin{document}")
        content = latex_content[start:end].strip()

        content = content.replace("\\maketitle", title_block)

        # Process the content
        html_content = process_latex_content(content)

        html_content = html_template.replace("CONTENT_PLACEHOLDER", html_content)
        os.makedirs(os.path.dirname(output_html), exist_ok=True)

        with open(output_html, 'w') as output_file:
            output_file.write(html_content)

        print(f"HTML file created successfully: {output_html}")

    except Exception as e:
        print(f"An error occurred while processing the file '{latex_file}': {e}")
        raise

def process_latex_content(content):
    # Remove comments
    content = re.sub(r"%.*", "", content)

    # Replace \vspace with line breaks
    content = re.sub(r"\\vspace\*?\{\s*.*?\s*\}", "<br>", content)

    # Handle LaTeX commands
    content = content.replace('\\\\', '<br>')
    content = re.sub(r"\\section\{(.*?)\}", r"<h2>\1</h2>", content)
    content = re.sub(r"\\subsection\{(.*?)\}", r"<h3>\1</h3>", content)
    content = re.sub(r"\\subsubsection\{(.*?)\}", r"<h4>\1</h4>", content)
    content = re.sub(r"\\emph\{(.*?)\}", r"<em>\1</em>", content)
    content = re.sub(r"\\textbf\{(.*?)\}", r"<strong>\1</strong>", content)
    content = re.sub(r"\\textit\{(.*?)\}", r"<em>\1</em>", content)
    content = content.replace("\\noindent", "")

    # Split content into paragraphs
    paragraphs = [f"<p>{para.strip()}</p>" for para in content.split("\n\n") if para.strip()]

    return "\n".join(paragraphs)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 latex-to-html.py <latex_file> <output_html> <css_path>")
        sys.exit(1)

    latex_file = sys.argv[1]
    output_html = sys.argv[2]
    css_path = sys.argv[3]

    try:
        latex_to_html(latex_file, output_html, css_path)
    except Exception as e:
        print(f"Error: {e}")