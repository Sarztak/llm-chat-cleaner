from loguru import logger
from rich.traceback import install
from pathlib import Path

install()
from bs4 import Tag, BeautifulSoup
from parse_chat import process_children, check_navigable_string
from md_to_tex_pipeline import convert_from_tex_to_pdf


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
    elif element.get("data-turn", "") == "assistant":
        header = "botresponse"
    else:
        return None  # do not process any other elements
    latex = process_children(element)
    return latex_block.format(header, latex, header)


def run_all_files():
    gpt_dir = Path("./gpt")
    (gpt_dir / "tex").mkdir(exist_ok=True, parents=True)
    (gpt_dir / "pdf").mkdir(exist_ok=True, parents=True)

    for html_file_path in (gpt_dir / "html").glob("*.html"):
        logger.info(f"File name: {html_file_path.name}")

        with open(html_file_path, "r", encoding="utf8") as fp:
            html = fp.read()

        latex = chat_html_to_latex(html)

        with open(
            gpt_dir / f"tex/{html_file_path.stem}.tex", "w", encoding="utf8"
        ) as w:
            w.write(latex)
        logger.info(f"File {html_file_path.stem}.tex written")
    convert_from_tex_to_pdf(tex_dir=gpt_dir / "tex", pdf_dir=gpt_dir / "pdf")

def test_one_file():
    html_file_path = Path("./drones - Branch · Branch · Skybrush Studio API.html")
    with open(html_file_path, "r", encoding="utf8") as fp:
        html = fp.read()
    latex = chat_html_to_latex(html)

    with open("index.tex", "w", encoding="utf8") as w:
        w.write(latex)

if __name__ == "__main__":
    cwd = Path.cwd()
    logger.add(cwd / "logs/chat_gpt_parse.log", mode="w")
    run_all_files()
