from rich.traceback import install
from typing import Any

install()
from bs4 import BeautifulSoup, NavigableString, Tag
import re
from convert_math import *

def check_navigable_string(element: Tag) -> str | None:
    if isinstance(element, NavigableString):
        return clean_and_esc_ele_text(element.string)
    return None

def escape_latex_text(text: str) -> str:
    pattern = re.compile(r"([\\{}$&$%_#])")
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


def clean_and_esc_ele_text(element: Any[Tag, str], escape: bool = True) -> str:
    # there are two cases if the elements is already a string then return the string else extract it
    text = element.get_text() if isinstance(element, Tag) else element
    cleaned_text = clean_text(text)
    if escape: # escape is not necessary when the text is code 
        text = escape_latex_text(text)
    return cleaned_text


def process_inline_elements(element: Tag) -> str:
    if (result := check_navigable_string(element)) is not None:
        return result

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

    processed_elements: list[str] = []

    for ele in element.children:
        text = clean_and_esc_ele_text(
            ele
        )  # remove extra whitespaces and escape special characters
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


def process_list_elements(element, ordered=False):
    if (result := check_navigable_string(element)) is not None:
        return result

    list_type = "enumerate" if ordered else "itemize"
    li_list = [f"\\begin{{{list_type}}}"]
    for li in element.children:
        # process each li element
        if li.name == "li":
            text = process_children(li) # I want this to recurse and parse children
            item_text = f"\\item {text}"
            li_list.append(item_text)
    # append begin itemize end itemize
    li_list.append(f"\\end{{{list_type}}}")
    li_block = "\n".join(li_list)
    return li_block


def process_children(element):
    if (result := check_navigable_string(element)) is not None:
        return result

    text_block = []

    for child in element.children:
        if child.name == "p": # a p tag can only contain inline elements
            p_text = process_inline_elements(child)
            text_block.append(p_text)
        elif child.name == "ul":
            # get all the immediate children which are li elements
            ul_block = process_list_elements(child, ordered=False)
            text_block.append(ul_block)
        elif child.name == "ol":
            ol_block = process_list_elements(child, ordered=True)
            text_block.append(ol_block)
        elif child.name == "code":
            text = clean_and_esc_ele_text(child, escape=False)
            if is_math_expression(text):
                # convert to inline math
                math_latex = convert_math_to_latex(text)
                text_block.append(f"${math_latex}$")
            else:
                text_block.append(
                    "\\begin{lstlisting}[breaklines=true, breakatwhitespace=false]\n"
                )
                text_block.append(text)
                text_block.append("\\end{lstlisting}")
        elif child.name == "br":
            text_block.append(
                " "
            )  # an extra line break will be added; but this is a fragile way to do it as it relies on \n being added at the very end. I need to find a better way
        else:
            div_text = process_children(
                child
            ).strip()  # I don't need the extra lines added between blocks due to recursion
            text_block.append(div_text)

    # remove empty string from the text block
    text_block = [t for t in text_block if t]
    return "\n\n".join(
        text_block
    )  # I need one blank line between the children of the same div


def main():
    with open("sevis.html", "r", encoding="utf8") as fp:
        html_parser = BeautifulSoup(
                fp, "html.parser", multi_valued_attributes=None
        )

    divs = html_parser.find_all("div")
    messages = []
    for div in divs:
        if div.get("data-testid", "") == "user-message":
            div_text = process_children(div)
            messages.append(f"\\begin{{userprompt}}\n{div_text}\n\\end{{userprompt}}")
        elif div.get("class", "").startswith(
            "font-claude-response"
        ):  # the font-claude-response can change, earlier it ws font-claude-message
            div_text = process_children(div)
            messages.append(f"\\begin{{botresponse}}\n{div_text}\n\\end{{botresponse}}")
    latex = "\n\n".join(
        messages
    )  # I need one blank line between the div elements in the latex format

    with open("sevis_chat.tex", "w", encoding="utf8") as w:
        for line in latex:
            w.write(line)


if __name__ == "__main__":
    main()
