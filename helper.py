import re


def escape_latex_text(s):
    pattern = re.compile(r"([\\{}&$%_#])")
    return pattern.sub(r"\\\1", s)


def process_inline_text(text: str) -> str:
    """
    This is supposed to returned text in latex format and does so recursively.
    When there is just one word that can be rendered in latex then that is the base case.
    """
    pattern_dict = {
        "bold": {
            "outer": r"""(?P<bold>\*\*[^*]+\*\*)""",
            "inner": re.compile(r"""\*\*([^*]+)\*\*"""),
            "latex": r"\textbf{{{}}}",
        },
        "italic": {
            "outer": r"""(?<!\*)(?P<italic>\*(?!\*)[^*]+\*)""",
            "inner": re.compile(r"""\*([^*]+)\*"""),
            "latex": r"\textit{{{}}}",
        },
        "code": {
            "outer": r"""(?<!`)(?P<code>`(?!`)[^`]+`)""",
            "inner": re.compile(r"""`([^`]+)`"""),
            "latex": r"\seqsplit{{{}}}",
        },
        "math": {
            "outer": r"""(?P<math>(?P<math_delim>\${1,2}).*?(?P=math_delim))""",
            "inner": re.compile(r"""((\${1,2})(.*?)\2)"""),
            "latex": "${}$",
        },
    }

    combined_pattern = re.compile(
        "|".join(pattern_dict[k]["outer"] for k in pattern_dict),
        re.MULTILINE,
    )
    splits = re.split(combined_pattern, text)

    processed_splits = []
    for split in splits:
        if split and split.strip():
            m = re.search(combined_pattern, split)
            if m:
                m = re.search(combined_pattern, split)
                for split_type in ["bold", "italic", "code", "math"]:
                    if m and m.group(split_type):
                        inner_match = re.search(
                            pattern_dict[split_type]["inner"], split
                        )
                        if inner_match:
                            inner_text = inner_match.groups()[-1]
                            inner_text = process_inline_text(inner_text)
                            inner_text_tex_format = pattern_dict[split_type][
                                "latex"
                            ].format(inner_text)
                            processed_splits.append(inner_text_tex_format)
            else:
                processed_splits.append(
                    escape_latex_text(split)
                )  # I realized that this is only thing which is needed for the base condition because in case of m being None is itself the base case

    return "".join(processed_splits)


def escape_long_tokens(text: str, threshold: int = 40) -> str:
    """This was supposed to help but it didn't help that much"""
    words = text.split()
    result = []
    for word in words:
        if len(word) > threshold:
            result.append(rf"\seqsplit{{{word}}}")
        else:
            result.append(word)
    return " ".join(result)
