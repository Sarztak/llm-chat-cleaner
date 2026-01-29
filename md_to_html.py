import markdown
import re

if __name__ == "__main__":
    with open('assorted 1.md', 'r', encoding='utf8') as fp:
        lines = fp.readlines()
    markdown_text = "".join(lines)
    code_pattern = r"""^\s*```([\s\S]*?)```$"""
    ol_pattern = r"""^(\d+\.\s.*(?:\n*\d+\.\s.*)*)"""
    test_ol_pattern = re.compile(r"""^(\d+)\.\s(.*)""", re.M)
    ul_pattern = r"""^(-\s.*(?:\n*-\s.*)*)*"""
    ol_elements = []
    prev_match1 = -1
    prev_match2 = ""
    running_text = ""

    for m in test_ol_pattern.finditer(markdown_text):
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
            match = pattern.search(markdown_text)
            running_text = running_text + match.group(1) + f"{curr_match1}. {curr_match2}" 
        elif int(prev_match1) == -1:
            running_text = f"{curr_match1}. {curr_match2}" # for the first list we need to start with something
        
        prev_match1 = curr_match1
        prev_match2 = curr_match2
    with open('md_to_html_op.txt', 'w', encoding='utf8') as w:
        for line in ol_elements:
            w.write(line + '\n\n-----------------------------------------\n\n')
    # splits = re.split(code_pattern, markdown_text, flags=re.MULTILINE)    
    # html = markdown.markdown(markdown_text, extensions=['fenced_code'])
    # with open('assorted_1.html', 'w', encoding='utf8') as wp:
    #     wp.write(html)