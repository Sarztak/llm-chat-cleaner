from rich.traceback import install

install()
from pathlib import Path
import argparse
from bs4 import Tag, BeautifulSoup
from convert_math import *
from parse_chat import *
import os
import shutil
from PIL import Image
from md_to_tex_pipeline import convert_from_tex_to_pdf
from parse_chat import process_children, check_navigable_string

def fix_img_path(html: str) -> str:
    pattern = re.compile(
        r"""<img\s+([^>]*?)alt="([^"]+)"([^>]*?)src="([^"]+)"([^>]*?)>"""
    )

    def update_img_tag(match: re.Match[str]) -> str:
        cwd = Path.cwd()
        # old_src this path is relative to the current directory ; so something like ./xyz/abc
        # I need to construct the absolute path. Currently all the chats are stored in folder claude/html
        # claude folder has html, tex and pdf folders and the html folder has folders in which the images live
        # so the absolute path would be cwd / claude / html / old_src
        # pathlib Path will normalize the path even with ./xyz/abc
        # few other things to consider is that the src should not have an extension; those with extension are
        # not uploaded by the user
        # also .webp is the binary file format in which the images uploaded by the user are downloaded when the chat
        # is saved from the browser using save as file command
        # also .webp files are not rendered by latex therefore they need to be converted to png by using Image from PIL

        before_alt = match[1]
        alt_filename = match[2]
        between = match[3]
        old_src = match[4]
        after_src = match[5]

        if Path(old_src).suffix != "":  # if a suffix exists no need to add anything
            # return the same tag unchanged
            return f'<img {before_alt}alt="{alt_filename}"{between}src="{old_src}"{after_src}>'

        abs_old_src = str(cwd / "claude/html" / Path(old_src))
        abs_old_src = abs_old_src.replace("\\", "/")
        new_src = (
            abs_old_src + ".webp"
        )  # this is just something I found out that files are binary webp
        if os.path.exists(abs_old_src):
            # copy the binary file but with added extension .webp
            shutil.copy(abs_old_src, new_src)
            # open the webp file and then save with .png extension
            img = Image.open(new_src)
            img.save(abs_old_src + ".png", "PNG")
            new_img_tag = f'<img {before_alt}alt="{alt_filename}"{between}src="{abs_old_src}.png"{after_src}>'
        else:
            # if the path does not exists then there is no point of img tag because it will get to the
            # latex files and then cause error
            # since the path does to the .png or any other file referenced by the src does not exists
            return ""
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
    soup = BeautifulSoup("", "html.parser")

    if (result := check_navigable_string(element)) is not None:
        return result

    header = None
    latex_block = "\\begin{{{}}}\n\n{}\n\n\\end{{{}}}"
    if str(element.get("class", "")).startswith(("mb-1 mt-6 group", "mb-1 mt-1")):
        # the mb-1 mt-6 group or mb-1 mt-1 groups are fragile and they can change
        header = "userprompt"
        # it can so happen that whenever I paste a very large content into the chat claude will only display a thumbnail.
        # in that case if I don't type into the dialog box, user-message tag does not exists and the program will error out
        chat_div = element.find("div", attrs={"data-testid": re.compile("user-message|file-thumbnail")})
        img_tags = element.find_all("img")
        new_tag = soup.new_tag("div")
        for img_tag in img_tags:
            new_tag.append(img_tag)
        new_tag.append(chat_div)
        element = new_tag  # needs to be reassigned because I am using the same name when passing to process_children
        # the font-claude-response can change, earlier it was font-claude-message
    elif str(element.get("class", "")).startswith(
        ("font-claude-response", "font-claude-message")
    ):
        header = "botresponse"
    else:
        return None  # do not process any other elements

    latex = process_children(element)
    return latex_block.format(header, latex, header)


def run_all_files():
    claude_dir = Path("./claude")
    (claude_dir / "tex").mkdir(exist_ok=True, parents=True)
    (claude_dir / "pdf").mkdir(exist_ok=True, parents=True)

    for html_file_path in (claude_dir / "html").glob("*.html"):

        with open(html_file_path, "r", encoding="utf8") as fp:
            html = fp.read()

        updated_html = fix_img_path(html)
        latex = chat_html_to_latex(updated_html)

        with open(
            claude_dir / f"tex/{html_file_path.stem}.tex", "w", encoding="utf8"
        ) as w:
            w.write(latex)
    convert_from_tex_to_pdf(tex_dir=claude_dir / "tex", pdf_dir=claude_dir / "pdf")

def test_one_file():
    cwd = Path.cwd()
    parse = argparse.ArgumentParser()
    parse.add_argument("file_path")
    args = parse.parse_args()
    html_file_path = Path(args.file_path)

    logger.info(f"file_path: {html_file_path}")

    file_name = html_file_path.stem # name of file without html extension
    with open(html_file_path, "r", encoding="utf8") as fp:
        html = fp.read()
    updated_html = fix_img_path(html)
    latex = chat_html_to_latex(updated_html)

    # create a directory to store the result
    out_dir = cwd / file_name
    out_dir.mkdir(exist_ok=True)

    # write output 
    with open(out_dir / f"{file_name}.tex", "w", encoding="utf8") as w:
        w.write(latex)

    convert_from_tex_to_pdf(tex_dir=out_dir, pdf_dir=out_dir)

if __name__ == "__main__":
    cwd = Path.cwd()
    logger.add(cwd / "logs/chat_claude_parse.log", mode="w")
    # run_all_files()
    test_one_file()
