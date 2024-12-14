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
    <title>{document_title}</title>
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
    """

    try:
        with open(latex_file, 'r') as file:
            latex_content = file.read()

        # Extract title, author, and date
        title_match = re.search(r"\\title\{(.*?)\}", latex_content, re.DOTALL)
        author_match = re.search(r"\\author\{(.*?)\}", latex_content, re.DOTALL)
        date_match = re.search(r"\\date\{(.*?)\}", latex_content, re.DOTALL)

        # Extract and format document title
        document_title = title_match.group(1).strip() if title_match else "Converted Document"

        # Create title block HTML
        title_block = ""
        if title_match:
            title_block += f"<h1>{html.escape(title_match.group(1).strip())}</h1>\n"
        if author_match:
            title_block += f"<h3>{html.escape(author_match.group(1).strip())}</h3>\n"
        if date_match:
            current_date = datetime.now().strftime("%B %d, %Y")
            date_text = date_match.group(1).replace("\\today", current_date).strip()
            title_block += f"<h4>{html.escape(date_text)}</h4>\n"

        # Replace \maketitle with the title block placeholder
        content = latex_content.replace("\\maketitle", "TITLE_PLACEHOLDER")

        # Extract body content between \begin{document} and \end{document}
        start = content.find("\\begin{document}")
        end = content.find("\\end{document}")

        if start == -1 or end == -1:
            raise ValueError("Could not find \\begin{document} or \\end{document} in the LaTeX file.")

        start += len("\\begin{document}")
        body_content = content[start:end].strip()

        # Process the LaTeX content into HTML
        html_content = process_latex_content(body_content)

        # Insert title block and replace placeholders
        html_content = html_content.replace("TITLE_PLACEHOLDER", title_block)
        final_html = html_template.format(document_title=html.escape(document_title), css_path=css_path)
        final_html = final_html.replace("CONTENT_PLACEHOLDER", html_content)

        # Write the final HTML to the output file
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
        # Check for environment start first
        if content.startswith("\\begin{", pos):
            env_match = re.match(r"\\begin\{(\w+\*?)\}", content[pos:])
            if env_match:
                env_name = env_match.group(1)
                env_content, new_pos = extract_environment(content, pos, env_name)
                pos = new_pos
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
                    # Math environment
                    html_output += f"$$\\begin{{{env_name}}}\n{env_content}\n\\end{{{env_name}}}$$"
                elif env_name in ["problem", "solution", "proof"]:
                    html_output += handle_custom_environment(env_name, env_content)
                else:
                    # Generic environment
                    html_output += process_latex_content(env_content, in_math_mode=in_math_mode)
            else:
                # Not a recognized environment, move forward
                pos += 1
        else:
            # Check for \left( or \right) first to avoid treating them as commands with braces
            special_delim_match = re.match(r"\\(left|right)(\(|\)|\[|\]|\{|\}|\\|\|)", content[pos:])
            if special_delim_match:
                direction = special_delim_match.group(1)  # 'left' or 'right'
                delimiter = special_delim_match.group(2)  # actual delimiter like ( or )
                pos += len(special_delim_match.group(0))
                if in_math_mode:
                    # Keep them as \left( or \right)
                    html_output += f"\\{direction}{delimiter}"
                else:
                    # Outside math mode, just show the delimiter character
                    html_output += delimiter
            else:
                # Now try a generic command
                command_match = re.match(r"\\(\w+)(\*?)(\{.*?\})?", content[pos:])
                if command_match:
                    command = command_match.group(1)
                    argument = command_match.group(3) if command_match.group(3) else ""
                    pos += len(command_match.group(0))
                    html_output += process_command(command, argument, in_math_mode=in_math_mode)
                else:
                    # No environment, no special delimiter, no command
                    # Treat the next characters as text until something else occurs
                    text_start = pos
                    while pos < length \
                          and not content.startswith("\\begin{", pos) \
                          and not re.match(r"\\(left|right)(\(|\)|\[|\]|\{|\}|\\|\|)", content[pos:]) \
                          and not re.match(r"\\(\w+)(\*?)(\{.*?\})?", content[pos:]):
                        pos += 1
                    text = content[text_start:pos]
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
            items.append(f"<li>{(item_content.strip())}</li>")
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

def handle_custom_environment(env_name, content):
    env_map = {
        "problem": "<div class='problem'><strong>Problem.</strong><br> {}</div>",
        "solution": "<div class='solution'><strong>Solution.</strong> {}</div>",
        "proof": "<div class='proof'><strong>Proof.</strong> {}<div class='qed'>∎</div></div><br>",
    }
    template = env_map.get(env_name, f"<div class='{env_name}'>{{}}</div>")
    processed_content = process_latex_content(content)
    return template.format(processed_content)

def process_command(command, argument, in_math_mode=False):
    arg_content = argument.strip()
    if arg_content.startswith('{') and arg_content.endswith('}'):
        arg_content = arg_content[1:-1].strip()

    if in_math_mode:
        if command == 'MakeUppercase':
            return arg_content.upper()
        elif command == 'mathbb':
            m = re.search(r'\\MakeUppercase\{([^}]*)\}', arg_content)
            if m:
                uppercase_text = m.group(1).upper()
                arg_content = re.sub(r'\\MakeUppercase\{[^}]*\}', uppercase_text, arg_content)
            return f"\\mathbb{{{arg_content}}}"
        elif command == 'mathcal':
            m = re.search(r'\\MakeUppercase\{([^}]*)\}', arg_content)
            if m:
                uppercase_text = m.group(1).upper()
                arg_content = re.sub(r'\\MakeUppercase\{[^}]*\}', uppercase_text, arg_content)
            return f"\\mathbb{{{arg_content}}}"
        else:
            return f"\\{command}{{{arg_content}}}"
    else:
        if command == 'MakeUppercase':
            # Outside math mode, just uppercase the argument
            return arg_content.upper()
        elif command == 'section':
            return f"<h2>{arg_content}</h2>"
        elif command == 'subsection':
            return f"<h3>{arg_content}</h3>"
        elif command == 'subsubsection':
            return f"<h4>{arg_content}</h4>"
        elif command in ['emph', 'textit']:
            return f"<em>{arg_content}</em>"
        elif command == 'textbf':
            return f"<strong>{arg_content}</strong>"
        elif command == 'noindent':
            return ''
        else:
            return f"\\{command}{{{arg_content}}}"

def process_text_block(text_block):
    # Identify math segments
    math_pattern = r'(\$\$.*?\$\$|\$.*?\$)'
    processed_parts = []
    last_end = 0

    for match in re.finditer(math_pattern, text_block, flags=re.DOTALL):
        start, end = match.span()
        # Text before math mode
        if start > last_end:
            pre_math_text = text_block[last_end:start].strip()
            if pre_math_text:
                # Split pre_math_text into paragraphs
                paragraphs = re.split(r'\n\s*\n', pre_math_text)
                for para in paragraphs:
                    para = process_text(para, in_math_mode=False)
                    if para:
                        processed_parts.append(f"<p>{para}</p>\n")
        math_segment = match.group(0)
        if math_segment.startswith('$$') and math_segment.endswith('$$'):
            inner = math_segment[2:-2]
            processed_math = process_latex_content(inner, in_math_mode=True)
            processed_parts.append(f"<p>$$\n{processed_math}\n$$</p>\n")
        else:
            inner = math_segment[1:-1]
            processed_math = process_latex_content(inner, in_math_mode=True)
            processed_parts.append(f"<p>${processed_math}$</p>\n")
        last_end = end

    # Remaining text after last math block
    if last_end < len(text_block):
        post_math_text = text_block[last_end:].strip()
        if post_math_text:
            # Split post_math_text into paragraphs
            paragraphs = re.split(r'\n\s*\n', post_math_text)
            for para in paragraphs:
                para = process_text(para, in_math_mode=False)
                if para:
                    processed_parts.append(f"<p>{para}</p>\n")

    return ''.join(processed_parts)

def process_text(text_part, in_math_mode=False):
    # In math mode, do not escape HTML or transform text
    if not in_math_mode:
        # Escape HTML for non-math text first
        text_part = html.escape(text_part)

        # Replace LaTeX markup with HTML tags (non-math text)
        text_part = re.sub(r"\\section\{(.*?)\}", r"<h2>\1</h2>", text_part)
        text_part = re.sub(r"\\subsection\{(.*?)\}", r"<h3>\1</h3>", text_part)
        text_part = re.sub(r"\\subsubsection\{(.*?)\}", r"<h4>\1</h4>", text_part)
        text_part = re.sub(r"\\emph\{(.*?)\}", r"<em>\1</em>", text_part)
        text_part = re.sub(r"\\textbf\{(.*?)\}", r"<strong>\1</strong>", text_part)
        text_part = re.sub(r"\\textit\{(.*?)\}", r"<em>\1</em>", text_part)
        text_part = re.sub(r"\\noindent", "", text_part)

        # Optionally, convert single newlines to <br> for line breaks within paragraphs
        # text_part = text_part.replace('\n', '<br>')

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