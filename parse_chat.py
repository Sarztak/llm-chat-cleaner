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
        latex = latex.strip()  
        if latex: # append only non empty string
            result.append(latex)

    return " ".join(result)

def process_list(element, ordered=False):
    _type = "enumerate" if ordered else "itemize"
    li_list = [f"\\begin{{{_type}}}"]
    if isinstance(element, NavigableString):
        return element.string
    for li in element.children:
        # process each li element
        if li.name == 'li':
            text = process_element(li)  
            item_text = f"\\item {text}" 
            li_list.append(item_text) 
    # append begin itemize end itemize
    li_list.append(f"\\end{{{_type}}}")
    li_block = "\n".join(li_list)
    return li_block

def process_div_children(div):
    text_block = []
    if isinstance(div, NavigableString):
        return div.string
    for child in div.children:
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
            text = clean_ele_text(child, escape=False) 
            text_block.append(f"\\begin{{lstlisting}}\n")
            text_block.append(text)
            text_block.append(f"\\end{{lstlisting}}")
        else:
            div_text = process_div_children(child)
            text_block.append(div_text)

    return "\n".join(text_block)

def main():
    with open('conversation.html', 'r', encoding='utf8') as fp:
        html_parser = BeautifulSoup(fp, 'html.parser',multi_valued_attributes=None)
    
    divs = html_parser.find_all('div', recursive=False)
    messages = []
    for div in divs:
        div_text = process_div_children(div)
        messages.append(div_text) 
        # if div.get('data-testid', "") == 'user-message':
        #     div_text = process_div_children(div)
        #     messages.append(div_text) 
        # elif div.get('class', "").startswith('font-claude-message'):
        #     div_text = process_div_children(div)
        #     messages.append(div_text) 

    latex = "\n\n".join(messages)

    with open('parse_chat_latex.tex', 'w', encoding='utf-8') as w:
        for line in latex:
            w.write(line)
if __name__ == "__main__":
    main()