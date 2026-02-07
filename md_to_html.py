import markdown
import re

def process_element(text):
    return text

def clean_ele_text(text):
    return text

def process_list(items, ordered=False):
    _type = "enumerate" if ordered else "itemize"
    li_list = [f"\\begin{{{_type}}}"]
    for item in items:
        text = process_element(item)  
        item_text = f"\\item {text}" 
        li_list.append(item_text) 
    li_list.append(f"\\end{{{_type}}}")
    li_block = "\n".join(li_list)
    return li_block


def capture_ol_pattern_with_inbetween(markdown_text):
    test_ol_pattern = re.compile(r"""^(\d+)\.\s(.*)""", re.M)
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

    return ol_elements

if __name__ == "__main__":
    with open('assorted 1.md', 'r', encoding='utf8') as fp:
        lines = fp.readlines()
    markdown_text = "".join(lines)
    user_block = re.compile(r"""^(?:User prompt .*)\n([\s\S]*?)\n\n^(?:GPT-4o mini:)""", re.M)
    bot_block = re.compile(r"""^(?:GPT-4o mini:)([\s\S]*?)\n(?:User prompt .*)""", re.M)
    code_pattern = re.compile(r"""^\s*```([\s\S]*?)```$""", re.M)
    ol_pattern = re.compile(r"""^(\d+\.\s.*(?:\n*\d+\.\s.*)*)""", re.M)
    ul_pattern = re.compile(r"""^(-\s.*(?:\n*-\s.*)*)*""", re.M)

    combined_pattern = re.compile(r"""^\s*```([\s\S]*?)```$|^(\d+\.\s.*(?:\n*\d+\.\s.*)*)|^(-\s.*(?:\n*-\s.*)*)*""", re.M)

    blocks = re.split(user_block, markdown_text)
    blocks = [block.strip() for block in blocks if block and block.strip()]

    # the first block is always the user block and the last block is always the llm response that is true in most cases and this will be assumed
    # so everything even numbered is user and odd numbered is llm response
    for i, block in enumerate(blocks):
        tex_elements = []

        # split each block by code, ol or ul list first
        splits = re.split(combined_pattern, markdown_text)
        splits = [split.split() for split in splits if split and split.strip()]
        for split in splits:
            text = ""
            # then detect code ol or ul block to process
            # at a time only one is true that is the assumption
            if re.search(ul_pattern, split):
                item_pattern = re.compile(r"""^(?:-\s*(.*)\n*)""", re.M)
                items = re.findall(item_pattern, split)
                if items:
                    text = process_list(items, ordered=False)
            elif re.search(code_pattern, split):
                text = clean_ele_text(split)
            elif re.search(ol_pattern, split):
                item_pattern = re.compile(r"""^(?:\d+\.\s*(.*)\n*)""", re.M)
                items = re.findall(item_pattern, split)
                if items:
                    text = process_list(items, ordered=True)
            else:
                text = process_element(split)

            if text: # append if not empty
                tex_elements.append(text)



    breakpoint()
    # now I want to split the text by these pattern 

    # with open('md_to_html_op.txt', 'w', encoding='utf8') as w:
    #     for line in ol_elements:
    #         w.write(line + '\n\n-----------------------------------------\n\n')
    # splits = re.split(code_pattern, markdown_text, flags=re.MULTILINE)    
    # html = markdown.markdown(markdown_text, extensions=['fenced_code'])
    # with open('assorted_1.html', 'w', encoding='utf8') as wp:
    #     wp.write(html)