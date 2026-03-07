import re


def capture_ol_pattern_with_inbetween(chat_text: str) -> list[str]:
    # this was a attempt to capture ordered/unordered lists in a different manner
    test_ol_pattern: re.Pattern[str] = re.compile(r"""^(\d+)\.\s(.*)""", re.M)
    ol_elements: list[str] = []
    prev_match1: str | None = None
    prev_match2: str | None = None
    running_text: str = ""

    m: re.Match[str]
    for m in test_ol_pattern.finditer(chat_text):
        curr_match1: str = m.group(1)
        curr_match2: str = m.group(2)

        if int(curr_match1) == 1 and running_text:
            # start of a new capture group
            # store the previous one
            ol_elements.append(running_text)
            running_text = f"{curr_match1}. {curr_match2}"

        elif prev_match1 is None:
            running_text = f"{curr_match1}. {curr_match2}"  # for the first list we need to start with something

        elif int(prev_match1) + 1 == int(curr_match1):
            assert isinstance(prev_match1, str) and isinstance(prev_match2, str)
            # expand the text and update the match
            regex_pattern: str = (
                rf"""{re.escape(prev_match1)}\.\s{re.escape(prev_match2)}([\s\S]*?){re.escape(curr_match1)}\.\s{re.escape(curr_match2)}"""
            )
            pattern: re.Pattern[str] = re.compile(regex_pattern, re.M)
            match: re.Match[str] | None = pattern.search(chat_text)
            if match:
                running_text = (
                    running_text + match.group(1) + f"{curr_match1}. {curr_match2}"
                )

        prev_match1 = curr_match1
        prev_match2 = curr_match2

    return ol_elements
