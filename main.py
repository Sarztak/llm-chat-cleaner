from rich.traceback import install; install()
from pathlib import Path
from html_to_markdown import convert
import mistune
from collections import Counter

def open_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as r:
        html = r.readlines()
        html = "\n".join(html)
    return html

def h2m(file_path, out_path):
        html = open_html(file_path, out_path)
        markdown = convert(html)
        with open(out_path, 'w', encoding='utf-8') as w:
            w.write(markdown)

def get_ast_from_markdown(file_path):
    html = open_html(file_path)
    markdown = convert(html)
    mkd_parser = mistune.create_markdown(renderer='ast')
    mkd_ast = mkd_parser(markdown)
    return mkd_ast

def strong(text):
    return f"\textbf{text}" 

def italic(text):
    return f"\textit{text}"

def _list(list_items):
    for l in list_items:
        # each l is a dictionary of type: list_item, and has children
        if l.get('type') == 'list_item':
            # the children it itself a list of dictionary with type and children
            for c in l.get('children'):
                if c.get('type') == 'block_text':
                    pass

def walk2(node):

    # if the type == 'text' then return the text in raw
    if set(node.keys()) == set(['type', 'raw']) and node['type'] == 'text':
        return node['raw']

    elif 'children' in node.keys():
        tex = ""
        for c in node.get('children'):
            # I would need a formatted string here so that I can pass it up the tree
            # so a formatted string which is raw which is unformatted
            formatted_raw = walk2(c) # empty dictionary is for collection operation
            node_copy = {k:v for k, v in node.items() if k != 'children'}
            _tex = apply_ops(node_copy, formatted_raw)
            tex = tex + _tex 

        # finally return the constructed string back
        return tex
    else:
        return ""


def apply_ops(ops, text):
    if not text or not ops:
        return ""
    # check ops and see what all exists type, attrs, bullets, etc
    tex = ""
    if 'type' in ops.keys():
        match ops['type']:
            case "strong":
                tex = f"\\textbr{{{text}}}" 
            case "emphasis":
                tex = f"\\textit{{{text}}}" 
            case "block_text":
                tex = f"{text}" # assuming that block_text resolves to raw string
            case "list_item":
                tex = f"\item {text}\n"
            case "list": # separating list is going to take more information like ordered or not
                if 'bullet' in ops.keys():
                    list_type = ops['bullet']
                    if list_type == '-':
                        tex = f"\\begin{{itemize}}\n{text}\end{{itemize}}\n"
                    elif list_type == '.':
                        tex = f"\\begin{{enumerate}}\n{text}\end{{enumerate}}\n"
            case "paragraph":
                tex = f"{text}\n"
            case "thematic_break":
                tex = f"{text}\n"
            case "blank_line": 
                tex = f"{text}\n"
            case _: # i still need to write cases for headers, underline and strikethrough
                tex = text 
    return tex


def walk(nodes, tokens, ops):
    if isinstance(nodes, dict):
        for k, v in nodes.items():
            if k == 'type':
                ops.append(v)
            elif k == 'raw':
                tokens.append((ops, v))
                ops = []
            elif isinstance(v, (list, dict)):
                walk(v, tokens, ops)
    elif isinstance(nodes, list):
        for l in nodes:
            walk(l, tokens, ops)

def collect(nodes, acc):
    if isinstance(nodes, dict):
        for k, v in nodes.items():
            if k == 'type':
                acc[v] += 1
            elif isinstance(v, (list, dict)):
                collect(v, acc)
    elif isinstance(nodes, list):
        for l in nodes:
            collect(l, acc)

def main():
    path = Path.cwd()
    file_path = path / "conversation.html"
    # h2m(file_path=file_path, out_path=path / "chat_convert_by_h2m.md")
    mkd_ast = get_ast_from_markdown(file_path)
    mkd_ast = {"type": "paragraph", "children": mkd_ast} # to make consistent data structure
    tex = walk2(mkd_ast)
    with open('formatted.tex', 'w', encoding='utf-8') as w:
        w.write(tex)
    # tokens, ops = [], []
    # walk(mkd_ast, tokens, ops)
    # breakpoint()
    # counter = Counter()    
    # collect(mkd_ast, counter)
    # print(counter)

if __name__ == "__main__":
    main()
    # mkd_parser = mistune.create_markdown(renderer='ast')
    # mkd_ast = mkd_parser("**_sarthak_**")