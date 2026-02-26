import re


def capture_ol_pattern_with_inbetween(chat_text):
    test_ol_pattern = re.compile(r"""^(\d+)\.\s(.*)""", re.M)
    ol_elements = []
    prev_match1 = -1
    prev_match2 = ""
    running_text = ""
    for m in test_ol_pattern.finditer(chat_text):
        curr_match1 = m.group(1)
        curr_match2 = m.group(2)

        if int(curr_match1) == 1 and running_text:
            # start of a new capture group
            # store the previous one
            ol_elements.append(running_text)
            running_text = f"{curr_match1}. {curr_match2}"
        elif int(prev_match1) + 1 == int(curr_match1):
            # expand the text and update the match
            regex_pattern = rf"""{re.escape(prev_match1)}\.\s{re.escape(prev_match2)}([\s\S]*?){re.escape(curr_match1)}\.\s{re.escape(curr_match2)}"""
            pattern = re.compile(regex_pattern, re.M)
            match = pattern.search(chat_text)
            running_text = (
                running_text + match.group(1) + f"{curr_match1}. {curr_match2}"
            )
        elif int(prev_match1) == -1:
            running_text = f"{curr_match1}. {curr_match2}"  # for the first list we need to start with something

        prev_match1 = curr_match1
        prev_match2 = curr_match2

    return ol_elements
