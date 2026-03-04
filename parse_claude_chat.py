from rich.traceback import install

install()
from pathlib import Path
from bs4 import Tag, BeautifulSoup
from convert_math import *
from parse_chat import *
import os
import shutil
from PIL import Image


def fix_img_path(html: str) -> str:
    pattern = re.compile(
        r"""<img\s+([^>]*?)alt="([^"]+)"([^>]*?)src="([^"]+)"([^>]*?)>"""
    )

    def update_img_tag(match):
        before_alt = match[1]
        alt_filename = match[2]
        between = match[3]
        old_src = match[4]
        after_src = match[5]
        # src_dir = Path(old_src).parent
        # new_src = src_dir / alt_filename
        new_src = old_src + ".webp"
        if os.path.exists(old_src):
            shutil.copy(old_src, new_src)
            img = Image.open(new_src)
            img.save(old_src + ".png", "PNG")
        new_img_tag = f'<img {before_alt}alt="{alt_filename}"{between}src="{old_src}.png"{after_src}>'
        return new_img_tag

    updated_html = pattern.sub(update_img_tag, html)
    return updated_html


def chat_html_to_latex(html: str) -> str:
    html_parser = BeautifulSoup(html, "html.parser", multi_valued_attributes=None)

    elements = html_parser.find_all("div")
    results = []
    for element in elements:
        processed_elements = process_chat_elements(element)

        if processed_elements is not None:
            results.append(processed_elements)

    return "\n\n".join(results)


def process_chat_elements(element: Tag) -> str | None:
    soup = BeautifulSoup('', 'html.parser')

    if (result := check_navigable_string(element)) is not None:
        return result

    header = None
    latex_block = "\\begin{{{}}}\n\n{}\n\n\\end{{{}}}"

    if element.get("class", "") == "mb-1 mt-6 group":
        header = "userprompt"
        chat_div = element.find('div', attrs={"data-testid": "user-message"})
        img_tags = element.find_all('img')
        new_tag = soup.new_tag('div')
        for img_tag in img_tags:
            new_tag.append(img_tag)
        new_tag.append(chat_div)
        element = new_tag # needs to be reassigned because I am using the same name when passing to process_children
        # the font-claude-response can change, earlier it was font-claude-message
    elif str(element.get("class", "")).startswith(
        ("font-claude-response", "font-claude-message")
    ):
        header = "botresponse"
    else:
        return None  # do not process any other elements

    latex = process_children(element)
    return latex_block.format(header, latex, header)


if __name__ == "__main__":
    html_file_path = Path(
        "./Presenting past work to non-technical researchers - Claude.html"
    )

    with open(html_file_path, "r", encoding="utf8") as fp:
        html = fp.read()
    updated_html = fix_img_path(html)
    latex = chat_html_to_latex(updated_html)

    with open("index.tex", "w", encoding="utf8") as w:
        w.write(latex)
