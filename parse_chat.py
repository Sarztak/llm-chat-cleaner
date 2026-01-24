from rich.traceback import install; install()
from bs4 import BeautifulSoup, NavigableString
import re 
from convert_math import *


def escape_latex_text(s):
    pattern = re.compile(r'([\\{}$&$%_#])')
    return pattern.sub(r'\\\1', s)

def clean_text(text):
    lines = text.split('\n') # separate the lines
    cleaned_lines = []
    pattern = r'[ \t]+' # remove extra tabs or white spaces
    for line in lines:
        line = re.sub(pattern, ' ', line)
        line = line.strip() # remove extra space in the beginning or end
        if line: # filter out empty lines
            cleaned_lines.append(line)
    return "\n\n".join(cleaned_lines)

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
        elif ele.name == 'code':
            inline_code = clean_ele_text(ele)
            latex = f"\\texttt{{{inline_code}}}"
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
            if is_math_expression(text):
                # convert to inline math
                math_latex = convert_math_to_latex(text)
                text_block.append(f"${math_latex}$")
            else:
                text_block.append(f"\\begin{{lstlisting}}[breaklines=true, breakatwhitespace=false]\n")
                text_block.append(text)
                text_block.append(f"\\end{{lstlisting}}")
        elif child.name == 'br':
            text_block.append(' ') # an extra line break will be added; but this is a fragile way to do it as it relies on \n being added at the very end. I need to find a better way
        else:
            div_text = process_div_children(child).strip() # I don't need the extra lines added between blocks due to recursion 
            text_block.append(div_text)
    
    # remove empty string from the text block
    text_block = [t for t in text_block if t]
    return "\n\n".join(text_block) # I need one blank line between the children of the same div

def main():
    with open('sevis.html', 'r', encoding='utf8') as fp:
        html_parser = BeautifulSoup(fp, 'html.parser',multi_valued_attributes=None)
    
    divs = html_parser.find_all('div')
    messages = []
    for div in divs:
        if div.get('data-testid', "") == 'user-message':
            div_text = process_div_children(div)
            messages.append(
                f"\\begin{{userprompt}}\n{div_text}\n\\end{{userprompt}}"
            )
        elif div.get('class', "").startswith('font-claude-response'): # the font-claude-response can change, earlier it ws font-claude-message
            div_text = process_div_children(div)
            messages.append(
                f"\\begin{{botresponse}}\n{div_text}\n\\end{{botresponse}}"
            )
    latex = "\n\n".join(messages) # I need one blank line between the div elements in the latex format
    
    with open('sevis_chat.tex', 'w', encoding='utf8') as w:
        for line in latex:
            w.write(line)

if __name__ == "__main__":
    main()