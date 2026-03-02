from rich.traceback import install
from pathlib import Path

install()
from bs4 import BeautifulSoup, NavigableString, Tag
import re
from convert_math import *

ele_to_tex_dict = {
    "strong": {
        "names": ("strong", "b"),
        "latex": r"\textbf{{{}}}",
    },
    "italic": {
        "names": ("em", "i"),
        "latex": r"\textit{{{}}}",
    },
    "code": {
        "names": ("code",),
        "latex": r"\texttt{{{}}}",
    },
    "url": {
        "names": ("a",),
        "latex": r"\href{{{}}}{{{}}}",
    },
}

inline_names = {name for entry in ele_to_tex_dict.values() for name in entry["names"]}


def is_inline_only(element: Tag) -> bool:
    if isinstance(element, NavigableString):
        return True
    elif all(
        isinstance(child, NavigableString) or child.name in inline_names
        for child in element.children
    ):
        return True
    else:
        return False


def check_navigable_string(element: Tag) -> str | None:
    if isinstance(element, NavigableString):
        return clean_and_esc_ele_text(element)


def escape_latex_text(text: str) -> str:
    pattern = re.compile(r"([\\{}&$%_#])")
    return pattern.sub(r"\\\1", text)


def clean_text(text: str) -> str:
    lines = text.split("\n")  # separate the lines
    cleaned_lines = []
    pattern = r"[ \t]+"  # remove extra tabs or white spaces
    for line in lines:
        line = re.sub(pattern, " ", line)
        line = line.strip()  # remove extra space in the beginning or end
        if line:  # filter out empty lines
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)  # I am joining by just one \n


def clean_and_esc_ele_text(
    element: Tag | NavigableString | str, escape: bool = True
) -> str:
    # there are two cases if the elements is already a string then return the string else extract it
    text = element.get_text() if isinstance(element, Tag) else element
    cleaned_text = clean_text(text)
    if escape:  # escape is not necessary when the text is code
        cleaned_text = escape_latex_text(cleaned_text)
    return cleaned_text


def process_inline_elements(element: Tag) -> str:
    if (result := check_navigable_string(element)) is not None:
        return result

    processed_elements: list[str] = []

    for ele in element.children:
        text = process_inline_elements(ele)
        latex = text
        for entry in ele_to_tex_dict.values():
            if ele.name in entry["names"]:
                if ele.name == "a":
                    href = ele.get("href", "")
                    latex = entry["latex"].format(href, text)
                else:
                    latex = entry["latex"].format(text)
                break

        latex = latex.strip()
        if latex:
            processed_elements.append(latex)
    return " ".join(processed_elements) if processed_elements else ""


def process_list_elements(element: Tag, ordered: bool = False) -> str:
    if (result := check_navigable_string(element)) is not None:
        return result

    list_type = "enumerate" if ordered else "itemize"
    li_list = [f"\\begin{{{list_type}}}"]
    for li in element.children:
        # process each li element
        if li.name == "li":
            text = process_children(li)  # I want this to recurse and parse children
            item_text = f"\\item {text}"
            li_list.append(item_text)
    # append begin itemize end itemize
    li_list.append(f"\\end{{{list_type}}}")
    li_block = "\n".join(li_list)
    return li_block


def process_children(element: Tag) -> str:
    if is_inline_only(element):
        return process_inline_elements(element)

    text_block = []

    for child in element.children:
        if child.name == "br":  # skip line breaks
            continue
        elif child.name == "p":  # a p tag can only contain inline elements
            text = process_children(child)
        elif child.name == "ul":
            # get all the immediate children which are li elements
            text = process_list_elements(child, ordered=False)
        elif child.name == "ol":
            text = process_list_elements(child, ordered=True)
        elif child.name == "code":
            text = clean_and_esc_ele_text(child, escape=True)
            # two version one with and one without escape is need because code can be match formula and it may not be
            # math formula does not require escape in some cases such as z_1 z subscript 1 but in some cases
            # it is actual name such as var_x
            text_no_esc = clean_and_esc_ele_text(child, escape=False)
            if is_math_expression(text_no_esc):
                # convert to inline math
                text = convert_math_to_latex(text_no_esc)
                text = f"${text}$"
            else:
                text = f"\\begin{{lstlisting}}[breaklines=true, breakatwhitespace=false]\n\n{text}\n\n\\end{{lstlisting}}"
        else:
            text = process_children(child)

        if text:
            text_block.append(text)

    return "\n\n".join(text_block)


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
    if (result := check_navigable_string(element)) is not None:
        return result

    header = None
    latex_block = "\\begin{{{}}}\n\n{}\n\n\\end{{{}}}"

    if element.get("data-testid", "") == "user-message":
        header = "userprompt"
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
    html_file_path = Path("./claude/html/Understanding .chm file format - Claude.html")

    with open(html_file_path, "r", encoding="utf8") as fp:
        html = fp.read()
    latex = chat_html_to_latex(html)

    with open("sevis_chat.tex", "w", encoding="utf8") as w:
        w.write(latex)
