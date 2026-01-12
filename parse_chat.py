from rich.traceback import install; install()
from bs4 import BeautifulSoup, NavigableString
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
    if isinstance(element, NavigableString):
        return element.string
    for ele in element.children:
        if ele.name == 'strong':
            text = clean_ele_text(ele) 
            latex = f"\\textbf{{{text}}}"
        elif ele.name in ('em', 'i'):
            text = clean_ele_text(ele) 
            latex = f"\\textit{{{text}}}"
        elif ele.name == 'a':
            href = ele.get('href', '')
            text = clean_ele_text(ele)
            latex = f"\\href{{{href}}}{{{text}}}"
        else:
            latex = clean_ele_text(ele)
        result.append(latex)

    return "\n".join(result)

def process_list(element, ordered=False):
    _type = "enumerate" if ordered else "itemize"
    li_list = [f"\begin{{{_type}}}"]
    if isinstance(element, NavigableString):
        return element.string
    for li in element.children:
        # process each li element
        text = process_element(li)  
        item_text = f"\item {text}" 
        li_list.append(item_text) 
    # append begin itemize end itemize
    li_list.append(f"\end{{{_type}}}")
    li_block = "\n".join(li_list)
    return li_block

def process_div_children(div):
    # breakpoint()
    text_block = []
    if isinstance(div, NavigableString):
        return div.string
    for child in div.children:
        if child.name == 'div':
            div_text = process_div_children(child)
            text_block.append(div_text)
        if child.name == 'p':
            p_text = process_element(child) 
            text_block.append(p_text)
        elif child.name == 'ul':
            # get all the immediate children which are li elements
            ul_block = process_list(child, ordered=False)
            text_block.append(ul_block)
        elif child.name == 'ol':
            ol_block = process_list(child, ordered=True)
            text_block.append(ol_block)
        elif child.name == 'code': 
            breakpoint()
            text = clean_ele_text(child, escape=False) 
            latex = f"\\texttt{{{text}}}"
            text_block.append(latex)
            pass
        else:
            plain_text = clean_ele_text(child) 
            text_block.append(plain_text)

    return "\n".join(text_block)

def main():
    with open('claude_stripped_down_chat.html', 'r', encoding='utf8') as fp:
        html_parser = BeautifulSoup(fp, 'html.parser',multi_valued_attributes=None)
    
    divs = html_parser.find_all('div')
    user_messages = []
    for div in divs:
        if div.get('data-testid', "") == 'user-message':
            div_text = process_div_children(div)
        elif div.get('class', "").startswith('font-claude-message'):
            div_text = process_div_children(div)
            pass

if __name__ == "__main__":
    main()