import re


def process_inline_text(text: str, processed_so_far: list) -> str:
    """
    This is supposed to returned text in latex format and does so recursively.
    When there is just one word that can be rendered in latex without modification then
    that is the base case
    """
    if processed_so_far and text == processed_so_far[-1]:
        return text

    # first process all the bold text
    # all text is inline so I am not using [\s\S] because that will capture newlines as well
    bold_pattern = r"""(?P<bold>\*\*[^*]+\*\*)"""
    # this is a tricky one because I need to distinguish between bold and italic. there a negative look ahead and look behind (?<!) (?!) assertion is needed to ensure that bold and italic are not confused.
    italic_pattern = r"""(?<!\*)(?P<italic>\*(?!\*)[^*]+\*)"""

    # highlight pattern; same as pattern for italic
    inline_code_pattern = r"""(?<!`)(?P<code>`(?!`)[^`]+`)"""

    # heading pattern
    heading_pattern = r"""(?P<heading>^#+\s+.*$)"""

    # inline math pattern
    math_pattern = r"""(?P<math>(?P<math_delim>\${1,2}).+(?P=math_delim))"""

    combined_pattern = re.compile(
        rf"{bold_pattern}|{italic_pattern}|{inline_code_pattern}|{url_pattern}|{heading_pattern}|{math_pattern}",
        re.MULTILINE,
    )

    splits = re.split(combined_pattern, text)
    splits = [split.strip() for split in splits if split and split.strip()]
    processed_text = ""

    for split in splits:
        m = re.search(combined_pattern, split)
        if m:
            if m.group("bold"):
                processed_text += extract_inner("bold", m.group("bold"))
            elif m.group("italic"):
                processed_text += extract_inner("italic", m.group("italic"))
            elif m.group("code"):
                processed_text += extract_inner("code", m.group("code"))
            elif m.group("url"):
                processed_text += extract_inner("url", m.group("url"))
            elif m.group("heading"):
                processed_text += extract_inner("heading", m.group("heading"))
            elif m.group("math"):
                processed_text += extract_inner("math", m.group("math"))
        else:
            processed_text += escape_latex_text(split)

    return processed_text, text

def extract_inner(group_name: str, text: str) -> str:
    bold_inner = re.compile(r"""(\*\*([^*]+)\*\*)""", re.M)
    italic_inner = re.compile(r"""(\*([^*]+)\*)""", re.M)
    code_inner = re.compile(r"""(`([^`]+)`)""", re.M)
    url_inner = re.compile(r"""(\[(.*?)\]\((.*?)\))""", re.M)
    heading_inner = re.compile(r"""(^(#+)\s+(.*)$)""", re.M)
    math_inner = re.compile(r"""((\${1,2})(.+)\2)""", re.M)

    processed_text = text
    match group_name:
        case "bold":
            inner = bold_inner.search(text)
            if inner:
                replacement_text = rf"\\textbf{{{text}}}"  # the replacement text needs to be a raw string because re.sub does its own escape processing on top of python's
                processed_text = _sub_pattern_to_tex(bold_inner, "bold", text)
        case "italic":
            inner = italic_inner.search(text)
            if inner:
                processed_text = _sub_pattern_to_tex(italic_inner, "italic", text)
        case "code":
            inner = code_inner.search(text)
            if inner:
                processed_text = _sub_pattern_to_tex(code_inner, "inline_code", text)
        case "url":
            inner = url_inner.search(text)
            if inner:
                processed_text = _sub_pattern_to_tex(url_inner, "href", text)
        case "heading":
            inner = heading_inner.search(text)
            if inner:
                processed_text = _sub_pattern_to_tex(heading_inner, "heading", text)
        case "math":
            inner = math_inner.search(text)
            if inner:
                processed_text = _sub_pattern_to_tex(math_inner, "math", text)
        case _:
            processed_text = text
    return processed_text

def _sub_pattern_to_tex(pattern, _type, text):

    def _tex(_type, text):
        match _type:
            case "bold":
                replacement_text = rf"\\textbf{{{text}}}"  # the replacement text needs to be a raw string because re.sub does its own escape processing on top of python's
            case "italic":
                replacement_text = rf"\\textit{{{text}}}"
            case "inline_code":
                replacement_text = rf"\\texttt{{{text}}}"
            case _:
                replacement_text = text
        return replacement_text

    matches = re.findall(pattern, text)

    for match in matches:
        if len(match) == 2:
            replacement_pattern = re.escape(match[0])
            inner_text = escape_latex_text(match[1])
            replacement_text = _tex(_type, inner_text)
            text = re.sub(replacement_pattern, replacement_text, text)
        elif len(match) == 3:
            if _type == "href":
                replacement_pattern = re.escape(match[0])
                url_part, inner_text = match[1], match[2]
                replacement_text = escape_latex_text(inner_text)
                replacement_text = rf"\\href{{{url_part}}}{{{replacement_text}}}"
                text = re.sub(replacement_pattern, replacement_text, text)
            elif _type == "heading":
                replacement_pattern = re.escape(match[0])
                hashes, inner_text = match[1], match[2]
                replacement_text = escape_latex_text(inner_text)
                heading_level = _get_heading_level(hashes)
                replacement_text = rf"{heading_level}{{{replacement_text}}}"
                text = re.sub(replacement_pattern, replacement_text, text)
    return text


"""
def process_inline_text(processed_text_list, text):
    if text == processed_text_list[-1]:
        return text
    # the idea is that if the text is just text and has nothing to process then the same thing is returned
    # if that is the case then we have reached the root and no more processing needs to be done
    # otherwise we call the process_inline_text on whatever was detected (each split)

"""


