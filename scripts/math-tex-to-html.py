import os
import re
import sys
from datetime import datetime
import html

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
                inlineMath: [['$','$']],
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
</head>
<body>
    <a href="../../index.html" class="home-button">Back</a>
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
        current_date = datetime.now().strftime("%B %d, %Y")  # Format: "Month Day, Year"

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
    content = re.sub(r"(?<!\\)%.*", "", content)

    # Initialize variables
    pos = 0
    length = len(content)
    html_output = ""

    while pos < length:
        if content.startswith("\\begin{", pos):
            # Start of an environment
            env_match = re.match(r"\\begin\{(\w+\*?)\}", content[pos:])
            if env_match:
                env_name = env_match.group(1)
                env_content, pos = extract_environment(content, pos, env_name)
                if env_name == "enumerate":
                    html_output += handle_enumerate(env_content)
                elif env_name == "itemize":
                    html_output += handle_itemize(env_content)
                elif env_name == "verbatim":
                    html_output += handle_verbatim(env_content)
                elif env_name == "lstlisting":
                    html_output += handle_lstlisting(env_content)
                elif env_name == "figure":
                    html_output += handle_figure(env_content)
                elif env_name in ['align', 'align*', 'equation', 'equation*', 'gather', 'multline', 'split']:
                    html_output += handle_math_environment(env_name, env_content)
                elif env_name in ["problem", "solution", "proof"]:
                    html_output += handle_custom_environment(env_name, env_content)
                else:
                    # Handle other environments as plain text for now
                    html_output += process_latex_content(env_content)
            else:
                pos += 1
        elif content.startswith("\\", pos):
            # Handle commands
            command_match = re.match(r"\\(\w+)(\*?)(\{.*?\})?", content[pos:])
            if command_match:
                command = command_match.group(1)
                star = command_match.group(2)
                argument = command_match.group(3) if command_match.group(3) else ""
                pos += len(command_match.group(0))
                html_output += process_command(command, argument)
            else:
                pos += 1
        else:
            # Regular text
            text = ""
            while pos < length and not content.startswith("\\begin{", pos) and not content.startswith("\\", pos):
                text += content[pos]
                pos += 1
            html_output += process_text_block(text)

    return html_output

def extract_environment(content, pos, env_name):
    # Extracts the content of an environment starting at pos
    start_tag = f"\\begin{{{env_name}}}"
    end_tag = f"\\end{{{env_name}}}"
    start_pos = pos + len(start_tag)
    depth = 1
    current_pos = start_pos
    while depth > 0 and current_pos < len(content):
        if content.startswith(start_tag, current_pos):
            depth += 1
            current_pos += len(start_tag)
        elif content.startswith(end_tag, current_pos):
            depth -= 1
            current_pos += len(end_tag)
            if depth == 0:
                return content[start_pos:current_pos - len(end_tag)], current_pos
        else:
            current_pos += 1
    raise ValueError(f"Environment '{env_name}' not closed properly")

def handle_enumerate(content):
    # Parses the content of an enumerate environment and returns HTML
    items = []
    pos = 0
    length = len(content)
    while pos < length:
        if content.startswith("\\item", pos):
            pos += len("\\item")
            # Skip optional argument after \item, if any
            if pos < length and content[pos] == '[':
                bracket_count = 1
                pos += 1
                while pos < length and bracket_count > 0:
                    if content[pos] == '[':
                        bracket_count += 1
                    elif content[pos] == ']':
                        bracket_count -= 1
                    pos += 1
            # Extract item content
            item_content = ""
            while pos < length:
                if content.startswith("\\item", pos) or content.startswith("\\end{", pos):
                    break
                elif content.startswith("\\begin{enumerate}", pos):
                    # Handle nested enumerate
                    nested_env_content, pos = extract_environment(content, pos, "enumerate")
                    nested_html = handle_enumerate(nested_env_content)
                    item_content += nested_html
                elif content.startswith("\\begin{itemize}", pos):
                    # Handle nested itemize
                    nested_env_content, pos = extract_environment(content, pos, "itemize")
                    nested_html = handle_itemize(nested_env_content)
                    item_content += nested_html
                else:
                    if content.startswith("\\begin{", pos):
                        # Handle other nested environments
                        env_match = re.match(r"\\begin\{(\w+\*?)\}", content[pos:])
                        if env_match:
                            env_name = env_match.group(1)
                            nested_env_content, pos = extract_environment(content, pos, env_name)
                            nested_html = process_latex_content(f"\\begin{{{env_name}}}{nested_env_content}\\end{{{env_name}}}")
                            item_content += nested_html
                        else:
                            item_content += content[pos]
                            pos += 1
                    else:
                        item_content += content[pos]
                        pos += 1
            items.append(f"<li>{process_latex_content(item_content.strip())}</li>")
        else:
            pos += 1  # Skip any whitespace or unexpected content
    return "<ol>\n" + "\n".join(items) + "\n</ol>"

def handle_itemize(content):
    # Similar to handle_enumerate but returns <ul>
    items = []
    pos = 0
    length = len(content)
    while pos < length:
        if content.startswith("\\item", pos):
            pos += len("\\item")
            # Skip optional argument after \item, if any
            if pos < length and content[pos] == '[':
                bracket_count = 1
                pos += 1
                while pos < length and bracket_count > 0:
                    if content[pos] == '[':
                        bracket_count += 1
                    elif content[pos] == ']':
                        bracket_count -= 1
                    pos += 1
            # Extract item content
            item_content = ""
            while pos < length:
                if content.startswith("\\item", pos) or content.startswith("\\end{", pos):
                    break
                elif content.startswith("\\begin{itemize}", pos):
                    # Handle nested itemize
                    nested_env_content, pos = extract_environment(content, pos, "itemize")
                    nested_html = handle_itemize(nested_env_content)
                    item_content += nested_html
                elif content.startswith("\\begin{enumerate}", pos):
                    # Handle nested enumerate
                    nested_env_content, pos = extract_environment(content, pos, "enumerate")
                    nested_html = handle_enumerate(nested_env_content)
                    item_content += nested_html
                else:
                    if content.startswith("\\begin{", pos):
                        env_match = re.match(r"\\begin\{(\w+\*?)\}", content[pos:])
                        if env_match:
                            env_name = env_match.group(1)
                            nested_env_content, pos = extract_environment(content, pos, env_name)
                            nested_html = process_latex_content(f"\\begin{{{env_name}}}{nested_env_content}\\end{{{env_name}}}")
                            item_content += nested_html
                        else:
                            item_content += content[pos]
                            pos += 1
                    else:
                        item_content += content[pos]
                        pos += 1
            items.append(f"<li>{process_latex_content(item_content.strip())}</li>")
        else:
            pos += 1  # Skip any whitespace or unexpected content
    return "<ul>\n" + "\n".join(items) + "\n</ul>"

def handle_verbatim(content):
    # Escape HTML special characters
    escaped_content = (
        content
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"<pre>{escaped_content}</pre>"
def handle_lstlisting(content):
    """
    Handle the content of a lstlisting environment, ensuring no LaTeX rendering
    or processing occurs, even if it contains square brackets or other special characters.
    """
    # Escape HTML and special characters to prevent rendering issues
    escaped_content = (
        content
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("{", "&#123;")  # Escaping '{'
        .replace("}", "&#125;")  # Escaping '}'
        .replace("[", "&#91;")  # Escaping '['
        .replace("]", "&#93;")  # Escaping ']'
    )
    # Wrap the escaped content in a preformatted block
    return f"<pre class='code-block'>{escaped_content}</pre>"

def handle_math_environment(env_name, content):
    return f"$$\\begin{{{env_name}}}\n{content}\n\\end{{{env_name}}}$$"

def handle_custom_environment(env_name, content):
    env_map = {
        "problem": "<div class='problem'><strong>Problem.</strong><br> {}</div>",
        "solution": "<div class='solution'><strong>Solution.</strong> {}</div>",
        "proof": "<div class='proof'><strong>Proof.</strong> {}<div class='qed'>∎</div></div><br>",
    }
    template = env_map.get(env_name, f"<div class='{env_name}'>{{}}</div>")
    processed_content = process_latex_content(content)
    return template.format(processed_content)
    

def handle_figure(content):
    includegraphics_match = re.search(r"\\includegraphics\[.*?\]\{(.*?)\}", content, re.DOTALL)
    caption_match = re.search(r"\\caption\{(.*?)\}", content, re.DOTALL)
    image_path = includegraphics_match.group(1).strip() if includegraphics_match else ""
    caption = caption_match.group(1).strip() if caption_match else ""
    caption_html = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f"""
    <figure>
        <img src="{image_path}" alt="{caption}" style="max-width:100\%;height:auto;">
        {caption_html}
    </figure>
    """

def process_command(command, argument):
    if command == 'section':
        return f"<h2>{argument[1:-1]}</h2>"
    elif command == 'subsection':
        return f"<h3>{argument[1:-1]}</h3>"
    elif command == 'subsubsection':
        return f"<h4>{argument[1:-1]}</h4>"
    elif command in ['emph', 'textit']:
        return f"<em>{argument[1:-1]}</em>"
    elif command == 'textbf':
        return f"<strong>{argument[1:-1]}</strong>"
    elif command == 'noindent':
        return ''
    elif command == '\\':
        return '<br>'
    else:
        # For other commands, return as is
        return f"\\{command}{argument}"

def process_text_block(text_block):
    # First, replace \vspace with a line break
    text_block = re.sub(r"\\vspace\*?\{\s*.*?\s*\}", "<br>", text_block)

    # Split text_block into text and math parts
    math_pattern = r'(\\\[.*?\\\]|\\\(.+?\\\)|\$\$.*?\$\$|\$(?:[^$\\]|\\.)+\$)'
    processed_parts = []
    last_end = 0
    for match in re.finditer(math_pattern, text_block, flags=re.DOTALL):
        start, end = match.span()
        if start > last_end:
            text_part = text_block[last_end:start]
            processed_parts.append(process_text(text_part))
        math_expr = match.group()
        processed_parts.append(math_expr)
        last_end = end
    if last_end < len(text_block):
        text_part = text_block[last_end:]
        processed_parts.append(process_text(text_part))
    return ''.join(processed_parts)

def process_text(text_part):
    # Handle LaTeX commands within text
    # text_part = text_part.replace('\\\\', '<br>')
    text_part = re.sub(r"\\section\{(.*?)\}", r"<h2>\1</h2>", text_part)
    text_part = re.sub(r"\\subsection\{(.*?)\}", r"<h3>\1</h3>", text_part)
    text_part = re.sub(r"\\subsubsection\{(.*?)\}", r"<h4>\1</h4>", text_part)
    text_part = re.sub(r"\\emph\{(.*?)\}", r"<em>\1</em>", text_part)
    text_part = re.sub(r"\\textbf\{(.*?)\}", r"<strong>\1</strong>", text_part)
    text_part = re.sub(r"\\textit\{(.*?)\}", r"<em>\1</em>", text_part)
    text_part = text_part.replace("\\noindent", "")
    # Replace special characters
    text_part = text_part.replace('&', '&amp;')
    text_part = text_part.replace('<', '&lt;')
    text_part = text_part.replace('>', '&gt;')
    return text_part

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