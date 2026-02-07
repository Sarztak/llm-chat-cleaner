import markdown
import re
from parse_chat import clean_ele_text

def process_inline_text(text):

    # first process all the  bold text
    # all text is inline so I am not using [\s\S] because that will capture newlines as well
    bold_pattern = re.compile(r"""(\*\*([^*]+)\*\*)""")

    # this is a tricky one because I need to distinguish between bold and italic. there a negative look ahead and look behind (?<!) (?!) assertion is needed to ensure that bold and italic are not confused.
    italic_pattern = re.compile(r"""(?<!\*)(\*(?!\*)([^*]+)\*)""")
    
    # highlight pattern; same as pattern for italic
    inline_code_pattern = re.compile(r"""(?<!`)(`(?!`)([^`]+)`)""")

    # href or url link pattern
    url_pattern = re.compile(r"""\[(.*?)\]\((.*?)\)""") 

    # now this will be repeated 3 times over one for each pattern

    def _sub_pattern_to_tex(pattern, _type, text):

        def _tex(_type, text):
            match _type:
                case "bold":
                    replacement_text = f"\\textbf{{{text}}}"
                case "italic":
                    replacement_text = f"\\textit{{{text}}}"
                case "inline_code":
                    replacement_text = f"\\texttt{{{text}}}"
                case _:
                    replacement_text = text
            return replacement_text

        matches = re.findall(pattern, text)

        for match in matches:
            if len(match) == 2:
                replacement_pattern = re.escape(match[0])
                replacement_text = _tex(_type, match[1])
                text = re.sub(replacement_pattern, replacement_text, text)

        return text

    text = _sub_pattern_to_tex(bold_pattern, "bold", text)
    text = _sub_pattern_to_tex(italic_pattern, "italic", text)
    text = _sub_pattern_to_tex(inline_code_pattern, "inline_code", text)

    # still need to process href and links
    return text


def process_list(items, ordered=False):
    _type = "enumerate" if ordered else "itemize"
    li_list = [f"\\begin{{{_type}}}"]
    for item in items:
        text = process_inline_text(item)  
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
    ul_pattern = re.compile(r"""^(-\s.*(?:\n*-\s.*)*)""", re.M)

    combined_pattern = re.compile(r"""^\s*```([\s\S]*?)```$|^(\d+\.\s.*(?:\n*\d+\.\s.*)*)|^(-\s.*(?:\n*-\s.*)*)""", re.M)

    blocks = re.split(user_block, markdown_text)
    blocks = [block.strip() for block in blocks if block and block.strip()]

    # the first block is always the user block and the last block is always the llm response that is true in most cases and this will be assumed
    # so everything even numbered is user and odd numbered is llm response
    processed_blocks = []
    for i, block in enumerate(blocks):
        tex_elements = []
        # split each block by code, ol or ul list first
        splits = re.split(combined_pattern, block)
        splits = [split.strip() for split in splits if split and split.strip()]
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
                inline_code = clean_ele_text(split, escape=False)
                text = f"\\texttt{{{inline_code}}}"
            elif re.search(ol_pattern, split):
                item_pattern = re.compile(r"""^(?:\d+\.\s*(.*)\n*)""", re.M)
                items = re.findall(item_pattern, split)
                if items:
                    text = process_list(items, ordered=True)
            else:
                text = clean_ele_text(split)

            if text: # append if not empty
                tex_elements.append(text)

        tex = "\n".join(tex_elements)

        if i % 2 == 0: # even response are users
            processed_block = f"\\begin{{userprompt}}\n{text}\n\\end{{userprompt}}"
        else:
            processed_block = f"\\begin{{botresponse}}\n{tex}\n\\end{{botresponse}}"
        
        processed_blocks.append(processed_block)

    # with open('md_to_html_op.txt', 'w', encoding='utf8') as w:
    #     for line in ol_elements:
    #         w.write(line + '\n\n-----------------------------------------\n\n')
    # splits = re.split(code_pattern, markdown_text, flags=re.MULTILINE)    
    # html = markdown.markdown(markdown_text, extensions=['fenced_code'])
    # with open('assorted_1.html', 'w', encoding='utf8') as wp:
    #     wp.write(html)