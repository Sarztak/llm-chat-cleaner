import re
from helper import process_inline_text
from rich.traceback import install

install()
from typing import Iterator, Tuple


def clean_text(text: str) -> str:
    lines = text.split("\n")  # separate the lines
    cleaned_lines = []
    pattern = r"[ \t]+"  # remove extra tabs or white spaces
    for line in lines:
        if line.startswith("---"):  # remove line breaks in markdown
            continue
        line = re.sub(pattern, " ", line)
        line = line.strip()  # remove extra space in the beginning or end
        if line:  # filter out empty lines
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)  # I am joining by just one \n


def list_to_tex(text: str, ordered: bool = False) -> str:
    if ordered:
        item_pattern = re.compile(r"""^(?:\d+\.\s*(.*)\n*)""", re.M)
        _type = "enumerate"
    else:
        item_pattern = re.compile(r"""^(?:-\s*(.*)\n*)""", re.M)
        _type = "itemize"
    items = re.findall(item_pattern, text)
    li_list = [f"\\begin{{{_type}}}"]
    for item in items:
        text = process_inline_text(item)
        item_text = f"\\item {text}"
        li_list.append(item_text)
    li_list.append(f"\\end{{{_type}}}")
    li_block = "\n".join(li_list)
    li_block_cleaned = clean_text(li_block)
    return li_block_cleaned


def iterate_user_bot_response(chat_text: str) -> Iterator[str]:
    block_split_pattern = re.compile(
        r"""^(?:User prompt .*)\n([\s\S]*?)\n\n^(?:GPT-4o mini:)""", re.M
    )

    blocks = re.split(block_split_pattern, chat_text)
    for block in blocks:
        if block and block.strip():
            yield block


def block_split_iterator(text_block: str) -> Iterator[Tuple[str, str]]:

    code_pattern = r"""^\s*(?P<code>```[\s\S]*?```)$"""
    ol_pattern = r"""^(?P<ol>\d+\.\s.*(?:\n*\d+\.\s.*)*)"""
    ul_pattern = r"""^(?P<ul>-\s.*(?:\n*-\s.*)*)"""
    heading_pattern = r"""(?P<heading>^#+\s+.*$)"""

    combined_pattern = re.compile(
        rf"""{code_pattern}|{ol_pattern}|{ul_pattern}|{heading_pattern}""",
        re.M,
    )
    splits = re.split(combined_pattern, text_block)

    for split in splits:
        if split and split.strip():
            matched = False
            m = re.search(combined_pattern, split)
            for split_type in ["heading", "code", "ol", "ul"]:
                if m and m.group(split_type):
                    split_text = m.group(split_type)
                    matched = True
                    yield split_type, split_text
                    break
            if not matched:
                yield "paragraph", split


def paragraph_to_tex(paragraph: str) -> str:
    # href or url link pattern
    url_pattern = r"""(?P<url>\[.*?\]\(.*?\))"""
    splits = re.split(url_pattern, paragraph)
    processed_splits = []
    for split in splits:
        if split and split.strip():
            m = re.search(url_pattern, split)
            if m and m.group("url"):
                _m = re.search(r"""(\[.*?\])(\(.*?\))""", split)
                if _m:
                    display_text = _m.group(0)  # only display_text should be processed
                    url = _m.group(1)  # no processing on the url part
                    processed_display_text = process_inline_text(display_text)
                    url_tex_format = rf"\\href{{{url}}}{{{processed_display_text}}}"
                    processed_splits.append(url_tex_format)
            else:
                paragraph_tex_format = process_inline_text(split)
                processed_splits.append(paragraph_tex_format)
    splits_joined = "".join(processed_splits)
    splits_joined_cleaned = clean_text(splits_joined)
    return splits_joined_cleaned


def code_to_tex(code: str) -> str:
    code = code.strip()
    code_pattern = re.compile(r"""```([\s\S+]*?)```""", re.M)
    m = re.search(code_pattern, code)
    text = ""
    if m:
        text = m.group(1)
    return f"\\begin{{lstlisting}}[breaklines=true, breakatwhitespace=false]\n\n{text}\n\n\\end{{lstlisting}}"


def heading_to_tex(heading: str) -> str:
    _, leading_hashes, text = re.split("^(#+)", heading)
    text = text.strip()
    n_hashes = len(leading_hashes)
    match n_hashes:
        case 1:
            heading_level = r"\section"
        case 2:
            heading_level = r"\subsection"
        case _ if n_hashes >= 3:
            heading_level = r"\subsubsection"
        case _:
            heading_level = ""
    formatted_text = paragraph_to_tex(text)

    return rf"{heading_level}{{{formatted_text}}}"


def process_blocks(chat_text: str) -> list:

    # the first block is always the user block and the last block is always the llm response that is true in most cases and this will be assumed so everything even numbered is user and odd numbered is llm response

    processed_blocks = []
    for i, block in enumerate(iterate_user_bot_response(chat_text=chat_text)):
        tex_elements = []
        block_header = "userprompt" if i % 2 == 0 else "botresponse"
        for split_type, split_text in block_split_iterator(block):
            text = ""
            if split_type == "heading":
                text = heading_to_tex(split_text)
            elif split_type == "code":
                text = code_to_tex(split_text)
            elif split_type == "ol":
                text = list_to_tex(split_text, ordered=True)
            elif split_type == "ul":
                text = list_to_tex(split_text, ordered=False)
            else:
                text = paragraph_to_tex(split_text)

            if text:  # append if not empty
                tex_elements.append(text)
        processed_block_text = "\n\n".join(tex_elements)
        processed_block_with_header = f"\\begin{{{block_header}}}\n\n{processed_block_text}\n\n\\end{{{block_header}}}"
        processed_blocks.append(processed_block_with_header)
    return processed_blocks


if __name__ == "__main__":
    with open("./markdown/o4 mini meltdown.md", "r", encoding="utf8") as fp:
        lines = fp.readlines()
    chat_text = "".join(lines)

    processed_chat = process_blocks(chat_text=chat_text)
    md_to_tex = "\n\n".join(processed_chat)

    with open("assorted.tex", "w", encoding="utf8") as w:
        for line in md_to_tex:
            w.write(line)
