from bs4 import BeautifulSoup
import re 

def escape_latex_text(s):
    pattern = re.compile(r'([\\{}$&$%_])')
    return pattern.sub(r'\\\1', s)

def clean_text(text):
    lines = text.split('\n')
    cleaned_lines = []
    pattern = r'[ \t]+'
    for line in lines:
        line = re.sub(pattern, ' ', line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def clean_ele_text(ele, escape=True):
    if isinstance(ele, str):
        text = clean_text(ele) # if the element is already a string 
    else:
        text = ele.get_text().strip() # if the element is not a string
    text = clean_text(text)
    if escape: # don't escape code blocks
        text = escape_latex_text(text)
    return text

def process_element(element):
    result = []
    for ele in element.children:
        if ele.name == 'strong':
            text = clean_ele_text(ele) 
            latex = f"\\textbf{{{text}}}"
        elif ele.name in ('em', 'i'):
            text = clean_ele_text(ele) 
            latex = f"\\textit{{{text}}}"
        elif ele.name == 'code':
            text = clean_ele_text(ele, escape=False) 
            latex = f"\\texttt{{{text}}}"
        elif ele.name == 'a':
            href = ele.get('href', '')
            text = clean_ele_text(ele)
            latex = f"\\href{{{href}}}{{{text}}}"
        else:
            latex = clean_ele_text(ele)
        result.append(latex)

def process_div_children(div):
    for child in div.children:
        if child.name == 'p':
            p_text = process_element(child) 
        elif child.name == 'ul':
            # append begin itemize end itemize
            pass
        elif child.name == 'ol':
            pass
def main():
    with open('claude_stripped_down_chat.html', 'r', encoding='utf8') as fp:
        html_parser = BeautifulSoup(fp, 'html.parser',multi_valued_attributes=None)
    
    divs = html_parser.find_all('div')
    user_messages = []
    for div in divs:
        if div.get('data-testid', "") == 'user-message':
            pass
        elif div.get('class', "").startswith('font-claude-message'):
            breakpoint()

if __name__ == "__main__":
    main()