from bs4 import BeautifulSoup
import re

def escape_latex(text):
    """Escape special LaTeX characters"""
    # Define replacements for special characters
    replacements = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    
    # Apply replacements
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text

def clean_text(text):
    """Clean text but preserve structure"""
    # Normalize whitespace within lines but preserve line breaks
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Collapse multiple spaces to single space
        line = re.sub(r'[ \t]+', ' ', line)
        cleaned_lines.append(line.strip())
    
    # Remove empty lines at start/end, but preserve internal ones
    while cleaned_lines and not cleaned_lines[0]:
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1]:
        cleaned_lines.pop()
    
    return '\n'.join(cleaned_lines)

def process_paragraph(p):
    """Process a single paragraph element"""
    result_parts = []
    
    for element in p.children:
        if isinstance(element, str):
            # Plain text - escape it
            text = element.strip()
            if text:
                result_parts.append(escape_latex(text))
        elif element.name == 'strong':
            # Bold text - escape content then wrap
            text = element.get_text().strip()
            if text:
                result_parts.append(f'\\textbf{{{escape_latex(text)}}}')
        elif element.name == 'em' or element.name == 'i':
            # Italic text - escape content then wrap
            text = element.get_text().strip()
            if text:
                result_parts.append(f'\\textit{{{escape_latex(text)}}}')
        elif element.name == 'code':
            # Code text - don't escape, just wrap
            text = element.get_text().strip()
            if text:
                result_parts.append(f'\\texttt{{{text}}}')
        elif element.name == 'a':
            # Hyperlink - format as \href{url}{text}
            href = element.get('href', '')
            text = element.get_text().strip()
            if href and text:
                result_parts.append(f'\\href{{{href}}}{{{escape_latex(text)}}}')
            elif text:
                result_parts.append(escape_latex(text))
        else:
            # Other tags - just get text and escape
            text = element.get_text().strip()
            if text:
                result_parts.append(escape_latex(text))
    
    return ' '.join(result_parts)

def convert_html_to_latex(html_content):
    """Convert HTML conversation to LaTeX format"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    latex_output = []
    
    # Find all main divs (each contains user or assistant)
    main_divs = soup.find_all('div', recursive=False)
    
    for main_div in main_divs:
        # Find speaker
        strong_tag = main_div.find('strong')
        if not strong_tag:
            continue
        
        speaker_text = strong_tag.get_text(strip=True).lower()
        if 'user' in speaker_text:
            speaker = 'user'
        elif 'assistant' in speaker_text:
            speaker = 'assistant'
        else:
            continue
        
        # Start environment
        if speaker == 'user':
            latex_output.append('\\begin{userprompt}')
        else:
            latex_output.append('\\begin{botresponse}')
        
        # Find content div (sibling after strong tag)
        content_div = strong_tag.find_next_sibling('div') or strong_tag.find_next('div')
        
        if content_div:
            # Process all paragraphs
            paragraphs = content_div.find_all('p', recursive=False)
            
            for p in paragraphs:
                para_text = process_paragraph(p)
                if para_text:
                    latex_output.append(para_text)
                    latex_output.append('')  # Blank line after each paragraph
            
            # Process unordered lists
            for ul in content_div.find_all('ul', recursive=False):
                latex_output.append('\\begin{itemize}')
                for li in ul.find_all('li', recursive=False):
                    item_text = escape_latex(clean_text(li.get_text()))
                    latex_output.append(f'\\item {item_text}')
                latex_output.append('\\end{itemize}')
                latex_output.append('')
            
            # Process ordered lists
            for ol in content_div.find_all('ol', recursive=False):
                latex_output.append('\\begin{enumerate}')
                for li in ol.find_all('li', recursive=False):
                    item_text = escape_latex(clean_text(li.get_text()))
                    latex_output.append(f'\\item {item_text}')
                latex_output.append('\\end{enumerate}')
                latex_output.append('')
        
        # Remove trailing blank line before closing
        if latex_output and latex_output[-1] == '':
            latex_output.pop()
        
        # Close environment
        if speaker == 'user':
            latex_output.append('\\end{userprompt}')
        else:
            latex_output.append('\\end{botresponse}')
        
        latex_output.append('')  # Blank line between speakers
    
    return '\n'.join(latex_output)

# Example usage
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Read from file
        input_file = sys.argv[1]
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        # Generate output filename
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            output_file = input_file.rsplit('.', 1)[0] + '.tex'
        
        latex_output = convert_html_to_latex(html_content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_output)
        
        print(f"Converted {input_file} -> {output_file}")
    else:
        print("Usage: python html_to_latex.py <input.html> [output.tex]")
        print("If output.tex is not specified, it will use input filename with .tex extension")