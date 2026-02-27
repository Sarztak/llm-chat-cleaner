import re

from md_to_html import escape_latex_text


def process_inline_text(text: str) -> str:
    """
    This is supposed to returned text in latex format and does so recursively.
    When there is just one word that can be rendered in latex without modification then
    that is the base case
    """
    pattern_dict = {
        "bold": {
            "outer": r"""(?P<bold>\*\*[^*]+\*\*)""",
            "inner": re.compile(r"""(\*\*([^*]+)\*\*)""", re.M),
            "latex": r"\\textbf{{{}}}",
        },
        "italic": {
            "outer": r"""(?<!\*)(?P<italic>\*(?!\*)[^*]+\*)""",
            "inner": re.compile(r"""(\*([^*]+)\*)""", re.M),
            "latex": r"\\textit{{{}}}",
        },
        "code": {
            "outer": r"""(?<!`)(?P<code>`(?!`)[^`]+`)""",
            "inner": re.compile(r"""(`([^`]+)`)""", re.M),
            "latex": r"\\texttt{{{}}}",
        },
        "math": {
            "outer": r"""(?P<math>(?P<math_delim>\${1,2}).+(?P=math_delim))""",
            "inner": re.compile(r"""((\${1,2})(.+)\2)""", re.M),
            "latex": "${}$",
        },
    }

    combined_pattern = re.compile(
        "|".join(pattern_dict[k]["outer"] for k in pattern_dict),
        re.MULTILINE,
    )
    splits = re.split(combined_pattern, text)
    splits = [split for split in splits if split and split.strip()]

    if (
        len(splits) <= 1
    ):  # if no splits are possible then there is nothing else to do except escape the text
        return escape_latex_text(text)

    processed_splits = []
    for split in splits:
        if split and split.strip():
            m = re.search(combined_pattern, split)
            if m:
                m = re.search(combined_pattern, split)
                for split_type in ["bold", "italic", "code", "math"]:
                    if m and m.group(split_type):
                        split_text = m.group(split_type)
                        inner_match = re.search(
                            pattern_dict[split_type]["inner"], split_text
                        )
                        if inner_match:
                            inner_text = inner_match.group(1)
                            inner_text = process_inline_text(inner_text)
                            inner_text_tex_format = pattern_dict[split_type][
                                "latex"
                            ].format(inner_text)
                            processed_splits.append(inner_text_tex_format)
            else:
                processed_splits.append(escape_latex_text(split))

    return "".join(processed_splits)
