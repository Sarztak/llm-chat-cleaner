import re
from helper import process_inline_text
from rich.traceback import install; install()
from typing import Iterator, Tuple

def escape_latex_text(s):
    pattern = re.compile(r"([\\{}$&$%_#])")
    return pattern.sub(r"\\\1", s)


def is_plain_text(s):
    return bool(re.fullmatch(r"[a-zA-Z0-9\\{}$&%_#\s]+", s))


def clean_text(text):
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


def list_to_tex(items, ordered=False):
    _type = "enumerate" if ordered else "itemize"
    li_list = [f"\\begin{{{_type}}}"]
    for item in items:
        text = process_inline_text(item, [])
        item_text = f"\\item {text}"
        li_list.append(item_text)
    li_list.append(f"\\end{{{_type}}}")
    li_block = "\n".join(li_list)
    return li_block


def iterate_user_bot_response(chat_text: str) -> Iterator[str]:
    block_split_pattern = re.compile(
        r"""^(?:User prompt .*)\n([\s\S]*?)\n\n^(?:GPT-4o mini:)""", re.M
    )

    blocks = re.split(block_split_pattern, chat_text)
    for block in blocks:
        if block and block.strip():
            yield block


def block_split_iterator(text_block: str) -> Iterator[Tuple[str, str]]:

    code_pattern = re.compile(r"""^\s*(?P<code>```[\s\S]*?```)$""", re.M)
    ol_pattern = re.compile(r"""^(?P<ol>\d+\.\s.*(?:\n*\d+\.\s.*)*)""", re.M)
    ul_pattern = re.compile(r"""^(?P<ul>-\s.*(?:\n*-\s.*)*)""", re.M)
    heading_pattern = re.compile(r"""(?P<heading>^#+\s+.*$)""", re.M)

    combined_pattern = re.compile(
        rf"""{code_pattern}|{ol_pattern}|{ul_pattern}|{heading_pattern}""",
        re.M,
    )

    splits = re.split(combined_pattern, text_block)
    for split in splits:
        if split and split.strip():
            m = re.search(combined_pattern, split)
            for split_type in ["heading", "code", "ol", "ul"]:
                if m and m.group(split_type):
                    split_text = m.group(split_type)
                    yield split_type, split_text
            yield "paragraph", split


def paragraph_to_tex(paragraph: str) -> str:
    # href or url link pattern
    url_pattern = r"""(?P<url>\[.*?\]\(.*?\))"""
    splits = re.split(url_pattern, paragraph)
    processed_splits = []
    for split in splits:
        if split and split.strip():
            m = re.search(url_pattern, split)
            if m and m.group('url'):
                _m = re.search(r"""(\[.*?\])(\(.*?\))""", split)
                if _m:
                    display_text = _m.group(0) # only display_text should be processed
                    url = _m.group(1) # no processing on the url part
                    processed_display_text = process_inline_text(display_text)
                    url_tex_format = rf"\\href{{{url}}}{{{processed_display_text}}}"
                    processed_splits.append(url_tex_format)
            else:
                paragraph_tex_format = process_inline_text(split)
                processed_splits.append(paragraph_tex_format)
    splits_joined = "".join(processed_splits)
    return splits_joined


def code_to_tex(code: str) -> str:
    code = code.strip()
    text = re.findall(r"""```(.+)```""", code)[0]
    text = clean_text(text)
    return f"\\begin{{lstlisting}}[breaklines=true, breakatwhitespace=false]\n\n{text}\n\n\\end{{lstlisting}}"


def heading_to_tex(heading: str) -> str:
    _, leading_hashes, text = re.split("^(#+)", heading)
    text = text.strip()
    n_hashes = len(leading_hashes)
    match n_hashes:
        case 1:
            heading_level = r"\\section"
        case 2:
            heading_level = r"\\subsection"
        case _ if n_hashes >= 3:
            heading_level = r"\\subsubsection"
        case _:
            heading_level = ""
    formatted_text = paragraph_to_tex(text)

    return rf"{heading_level}{{{formatted_text}}}"


if __name__ == "__main__":
    with open("assorted 1.md", "r", encoding="utf8") as fp:
        lines = fp.readlines()
    chat_text = "".join(lines)

    # the first block is always the user block and the last block is always the llm response that is true in most cases and this will be assumed so everything even numbered is user and odd numbered is llm response

    processed_blocks = []
    for i, block in enumerate(iterate_user_bot_response(chat_text=chat_text)):
        breakpoint()
        tex_elements = []
        block_header = 'userprompt' if i % 2 == 0 else 'botresponse'
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

            # then detect code ol or ul block to process
            # at a time only one is true that is the assumption
            # code pattern and code blocks are special because they don't need any processing
            # the combined pattern split into paragraph, ordered, and unordered lists
            # and code block and then we detect individual blocks using appropriate regex

            if text:  # append if not empty
                tex_elements.append(text)
        processed_block_text = "\n\n".join(tex_elements)    
        processed_block_with_header = f"\\begin{{{block_header}}}\n\n{processed_block_text}\n\n\\end{{{block_header}}}"
        processed_blocks.append(processed_block_with_header)

    md_to_tex = "\n\n".join(processed_blocks)

    with open("assorted.tex", "w", encoding="utf8") as w:
        for line in md_to_tex:
            w.write(line)
