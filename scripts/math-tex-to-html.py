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
        current_date = datetime.now().strftime("%B %d, %Y")

        # Extract preamble information for title, author, and date
        title_match = re.search(r"\\title\{(.*?)\}", latex_content, re.DOTALL)
        author_match = re.search(r"\\author\{(.*?)\}", latex_content, re.DOTALL)
        date_match = re.search(r"\\date\{(.*?)\}", latex_content, re.DOTALL)

        title_text = title_match.group(1).strip() if title_match else ""
        author_text = author_match.group(1).strip() if author_match else ""
        if date_match:
            date_text = date_match.group(1).replace("\\today", current_date).strip()
        else:
            date_text = ""

        # Create the title block HTML
        title_block = ""
        if title_text:
            title_block += f"<h1>{title_text}</h1>\n"
        if author_text:
            title_block += f"<h3>{author_text}</h3>\n"
        if date_text:
            title_block += f"<h4>{date_text}</h4>\n"

        # Replace \maketitle with a placeholder so it won't be processed/escaped
        content = latex_content.replace("\\maketitle", "TITLE_PLACEHOLDER")

        # Extract the body content between \begin{document} and \end{document}
        start = content.find("\\begin{document}")
        end = content.find("\\end{document}")

        if start == -1 or end == -1:
            raise ValueError("Could not find \\begin{document} or \\end{document} in the LaTeX file.")

        start += len("\\begin{document}")
        body_content = content[start:end].strip()

        # Process the LaTeX content
        html_content = process_latex_content(body_content)

        # Now insert the title block HTML after processing
        html_content = html_content.replace("TITLE_PLACEHOLDER", title_block)

        # Insert into the HTML template
        final_html = html_template.replace("CONTENT_PLACEHOLDER", html_content)
        os.makedirs(os.path.dirname(output_html), exist_ok=True)

        with open(output_html, 'w') as output_file:
            output_file.write(final_html)

        print(f"HTML file created successfully: {output_html}")

    except Exception as e:
        print(f"An error occurred while processing the file '{latex_file}': {e}")
        raise

def process_latex_content(content, in_math_mode=False):
    # Remove comments
    content = re.sub(r"(?<!\\)%.*", "", content)

    pos = 0
    length = len(content)
    html_output = ""

    while pos < length:
        if content.startswith("\\begin{", pos):
            env_match = re.match(r"\\begin\{(\w+\*?)\}", content[pos:])
            if env_match:
                env_name = env_match.group(1)
                env_content, pos = extract_environment(content, pos, env_name)
                if env_name == "enumerate":
                    html_output += handle_enumerate(env_content)
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
                    # Handle other environments as normal text
                    html_output += process_latex_content(env_content)
            else:
                pos += 1
        elif content.startswith("\\", pos):
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
            text = ""
            while pos < length and not content.startswith("\\begin{", pos) and not content.startswith("\\", pos):
                text += content[pos]
                pos += 1
            html_output += process_text_block(text)

    return html_output

def extract_environment(content, pos, env_name):
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
    items = []
    pos = 0
    length = len(content)
    while pos < length:
        if content.startswith("\\item", pos):
            pos += len("\\item")
            # Skip optional argument
            if pos < length and content[pos] == '[':
                bracket_count = 1
                pos += 1
                while pos < length and bracket_count > 0:
                    if content[pos] == '[':
                        bracket_count += 1
                    elif content[pos] == ']':
                        bracket_count -= 1
                    pos += 1
            item_content = ""
            while pos < length:
                if content.startswith("\\item", pos) or content.startswith("\\end{", pos):
                    break
                elif content.startswith("\\begin{enumerate}", pos):
                    nested_env_content, pos = extract_environment(content, pos, "enumerate")
                    nested_html = handle_enumerate(nested_env_content)
                    item_content += nested_html
                elif content.startswith("\\begin{itemize}", pos):
                    nested_env_content, pos = extract_environment(content, pos, "itemize")
                    nested_html = handle_itemize(nested_env_content)
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
            pos += 1
    return "<ol>\n" + "\n".join(items) + "\n</ol>"

def handle_verbatim(content):
    escaped_content = (
        content
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"<pre>{escaped_content}</pre>"

def handle_lstlisting(content):
    escaped_content = (
        content
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("{", "&#123;")
        .replace("}", "&#125;")
        .replace("[", "&#91;")
        .replace("]", "&#93;")
    )
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
        <img src="{image_path}" alt="{caption}" style="max-width:100%;height:auto;">
        {caption_html}
    </figure>
    """

def process_command(command, argument, in_math_mode=False):
    # Remove outer braces if present
    arg_content = argument.strip()
    if arg_content.startswith('{') and arg_content.endswith('}'):
        arg_content = arg_content[1:-1]

    # If in math mode, we want to do minimal transformations
    if in_math_mode:
        if command == 'MakeUppercase':
            # Convert the argument to uppercase and return it as plain text
            return arg_content.upper()
        elif command == 'mathbb':
            # Just return \mathbb{UPPERCASED_CONTENT} if needed
            # If the argument contained another command like \MakeUppercase,
            # you'd have processed it before calling process_command again.
            # Here, we assume arg_content is already processed.
            return f"\\mathbb{{{arg_content}}}"
        else:
            # For other commands inside math, return them as is
            return f"\\{command}{{{arg_content}}}"
    else:
        # Outside math mode, you may apply your existing HTML transformations if desired.
        if command == 'section':
            return f"<h2>{arg_content}</h2>"
        elif command == 'subsection':
            return f"<h3>{arg_content}</h3>"
        # ... other commands as before ...
        else:
            return f"\\{command}{{{arg_content}}}"

def process_text_block(text_block):
    # Identify math segments and handle them separately
    # For math mode sections, call process_command with in_math_mode=True.
    math_pattern = r'(\$\$(.*?)\$\$|\$(.*?)\$)'
    processed_parts = []
    last_end = 0

    for match in re.finditer(math_pattern, text_block, flags=re.DOTALL):
        start, end = match.span()
        # Text before math
        if start > last_end:
            text_part = text_block[last_end:start]
            processed_parts.append(process_text(text_part))  # normal text processing
        math_segment = match.group(0)
        
        # Now process math_segment as in-math-mode content
        math_content = math_segment.strip('$')
        # Process math content with in_math_mode=True
        processed_math = process_latex_content(math_content, in_math_mode=True)
        
        # Re-wrap processed math in $...$ or $$...$$ depending on original delimiter
        if math_segment.startswith('$$'):
            processed_parts.append(f"$${processed_math}$$")
        else:
            processed_parts.append(f"${processed_math}$")
        last_end = end

    # Remaining text after last math block
    if last_end < len(text_block):
        text_part = text_block[last_end:]
        processed_parts.append(process_text(text_part))

    return ''.join(processed_parts)


def process_text(text_part):
    # Replace LaTeX markup with HTML tags (non-math text)
    text_part = re.sub(r"\\section\{(.*?)\}", r"<h2>\1</h2>", text_part)
    text_part = re.sub(r"\\subsection\{(.*?)\}", r"<h3>\1</h3>", text_part)
    text_part = re.sub(r"\\subsubsection\{(.*?)\}", r"<h4>\1</h4>", text_part)
    text_part = re.sub(r"\\emph\{(.*?)\}", r"<em>\1</em>", text_part)
    text_part = re.sub(r"\\textbf\{(.*?)\}", r"<strong>\1</strong>", text_part)
    text_part = re.sub(r"\\textit\{(.*?)\}", r"<em>\1</em>", text_part)
    text_part = text_part.replace("\\noindent", "")

    # Escape only '&' here (to avoid breaking HTML entities),
    # Leave < and > alone so HTML tags remain intact.
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