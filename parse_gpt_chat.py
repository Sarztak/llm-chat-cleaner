from rich.traceback import install
from pathlib import Path

install()
from bs4 import Tag
from convert_math import *
from parse_chat import *


def chat_html_to_latex(html: str) -> str:
    html_parser = BeautifulSoup(html, "html.parser", multi_valued_attributes=None)

    elements = html_parser.find_all("article")

    results = []
    for element in elements:
        processed_elements = process_chat_elements(element)

        if processed_elements is not None:
            results.append(processed_elements)

    return "\n\n".join(results)


def process_chat_elements(element: Tag) -> str | None:
    if (result := check_navigable_string(element)) is not None:
        return result

    header = None
    latex_block = "\\begin{{{}}}\n\n{}\n\n\\end{{{}}}"
    if element.get("data-turn", "") == "user":
        header = "userprompt"
        # the font-claude-response can change, earlier it was font-claude-message
    elif element.get("data-turn", "") == "assistant":
        header = "botresponse"
    else:
        return None  # do not process any other elements
    latex = process_children(element)
    return latex_block.format(header, latex, header)


if __name__ == "__main__":
    html_file_path = Path("./drones - Branch · Branch · Skybrush Studio API.html")
    with open(html_file_path, "r", encoding="utf8") as fp:
        html = fp.read()
    latex = chat_html_to_latex(html)

    with open("index.tex", "w", encoding="utf8") as w:
        w.write(latex)
