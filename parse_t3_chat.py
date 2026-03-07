from loguru import logger
from rich.traceback import install
from pathlib import Path

install()
from bs4 import Tag, BeautifulSoup
from convert_math import *
from parse_chat import *
from md_to_tex_pipeline import convert_from_tex_to_pdf
from parse_chat import process_children, check_navigable_string

def chat_html_to_latex(html: str) -> str:
    """This function finds the top level element which may be a div/article etc that contains user/assistant text"""
    html_parser = BeautifulSoup(html, "html.parser", multi_valued_attributes=None)

    # for t3 chat there are two divs with attributes role & aria-label
    # role is set to "article" and aria-label is set to Your message: and Assistant message: 
    # this will be used to filter out the relevant elements
    elements = html_parser.find_all("div", attrs={"role": "article"}) 

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
    if element.get("aria-label", "") == "Your message":
        header = "userprompt"
    elif element.get("aria-label", "") == "Assistant message":
        header = "botresponse"
    else:
        return None  # do not process any other elements
    latex = process_children(element)
    return latex_block.format(header, latex, header)


def run_all_files():
    t3_dir = Path("./t3")
    (t3_dir / "tex").mkdir(exist_ok=True, parents=True)
    (t3_dir / "pdf").mkdir(exist_ok=True, parents=True)

    for html_file_path in (t3_dir / "html").glob("*.html"):
        logger.info(f"File name: {html_file_path.name}")

        with open(html_file_path, "r", encoding="utf8") as fp:
            html = fp.read()

        latex = chat_html_to_latex(html)

        with open(
            t3_dir / f"tex/{html_file_path.stem}.tex", "w", encoding="utf8"
        ) as w:
            w.write(latex)
        logger.info(f"File {html_file_path.stem}.tex written")
    convert_from_tex_to_pdf(tex_dir=t3_dir / "tex", pdf_dir=t3_dir / "pdf")

def test_one_file():
    html_file_path = Path("./t3/html/Help refining LaTeX code for pdflatex (removing xelatex_lualatex needs) - T3 Chat_files.html")
    with open(html_file_path, "r", encoding="utf8") as fp:
        html = fp.read()
    latex = chat_html_to_latex(html)

    with open("index.tex", "w", encoding="utf8") as w:
        w.write(latex)

if __name__ == "__main__":
    cwd = Path.cwd()
    logger.add(cwd / "logs/chat_t3_parse.log", mode="w")
    run_all_files()
