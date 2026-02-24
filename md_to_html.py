import re


def escape_latex_text(s):
    pattern = re.compile(r'([\\{}$&$%_#])')
    return pattern.sub(r'\\\1', s)

def clean_text(text):
    lines = text.split('\n') # separate the lines
    cleaned_lines = []
    pattern = r'[ \t]+' # remove extra tabs or white spaces
    for line in lines:
        if line.startswith('---'):# remove line breaks in markdown
            continue
        line = re.sub(pattern, ' ', line)
        line = line.strip() # remove extra space in the beginning or end
        if line: # filter out empty lines
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines) # I am joining by just one \n

def extract_inner(group_name: str, text: str) -> dict:
    bold_inner    = re.compile(r"""\*\*([^*]+)\*\*""", re.M)
    italic_inner  = re.compile(r"""\*([^*]+)\*""", re.M)
    code_inner    = re.compile(r"""`([^`]+)`""", re.M)
    url_inner     = re.compile(r"""\[(.*?)\]\((.*?)\)""", re.M)
    heading_inner = re.compile(r"""^(#+)\s+(.*)$""", re.M)
    math_inner    = re.compile(r"""(\${1,2})(.+)\1""", re.M)

    match group_name:
        case 'bold':
            inner = bold_inner.search(text)
            if inner:
                return {'text': inner.group(1)}
        case 'italic':
            inner = italic_inner.search(text)
            if inner:
                return {'text': inner.group(1)}
        case 'code':
            inner = code_inner.search(text)
            if inner:
                return {'text': inner.group(1)}
        case 'url':
            inner = url_inner.search(text)
            if inner:
                return {'label': inner.group(1), 'href': inner.group(2)}
        case 'heading':
            inner = heading_inner.search(text)
            if inner:
                return {'level': len(inner.group(1)), 'text': inner.group(2)}
        case 'math':
            inner = math_inner.search(text)
            if inner:
                return {'text': inner.group(2)}
    return {'text': text}

def process_inline_text(text):

    # first process all the bold text
    # all text is inline so I am not using [\s\S] because that will capture newlines as well
    bold_pattern    = r"""(?P<bold>\*\*[^*]+\*\*)"""
    # this is a tricky one because I need to distinguish between bold and italic. there a negative look ahead and look behind (?<!) (?!) assertion is needed to ensure that bold and italic are not confused.
    italic_pattern  = r"""(?<!\*)(?P<italic>\*(?!\*)[^*]+\*)"""
    
    # highlight pattern; same as pattern for italic
    inline_code_pattern = r"""(?<!`)(?P<code>`(?!`)[^`]+`)"""

    # href or url link pattern
    url_pattern     = r"""(?P<url>\[.*?\]\(.*?\))"""

    # heading pattern
    heading_pattern = r"""(?P<heading>^#+\s+.*$)"""

    # inline math pattern
    math_pattern    = r"""(?P<math>(?P<math_delim>\${1,2}).+(?P=math_delim))"""
    
    combined_pattern = re.compile(
        rf"{bold_pattern}|{italic_pattern}|{inline_code_pattern}|{url_pattern}|{heading_pattern}|{math_pattern}",
        re.MULTILINE
    )

    splits = re.split(combined_pattern, text)
    splits = [split.strip() for split in splits if split and split.strip()]
    for split in splits:
        m = re.search(combined_pattern, split)
        breakpoint()
        if m:
            if m.group('bold'):
                print(extract_inner('bold', m.group('bold')))
            elif m.group('italic'):
                print(extract_inner('italic', m.group('italic')))
            elif m.group('code'):
                print(extract_inner('code', m.group('code')))
            elif m.group('url'):
                print(extract_inner('url', m.group('url')))
            elif m.group('heading'):
                print(extract_inner('heading', m.group('heading')))
            elif m.group('math'):
                print(extract_inner('math', m.group('math')))
        else:
            print("text", split)

    def _sub_pattern_to_tex(pattern, _type, text):

        def _tex(_type, text):
            match _type:
                case "bold":
                    replacement_text = rf"\\textbf{{{text}}}" # the replacement text needs to be a raw string because re.sub does its own escape processing on top of python's
                case "italic":
                    replacement_text = rf"\\textit{{{text}}}"
                case "inline_code":
                    replacement_text = rf"\\texttt{{{text}}}"
                case _:
                    replacement_text = text
            return replacement_text

        matches = re.findall(pattern, text)

        def _get_heading_level(hashes):
            n_hash = len(re.findall('#', hashes))

            match n_hash:
                case 1:
                    heading_level = r"\\section"
                case 2:
                    heading_level = r"\\subsection"
                case _ if n_hash >= 3:
                    heading_level = r"\\subsubsection"
                case _:
                    heading_level = ""
            return heading_level
            
        for match in matches:
            if len(match) == 2:
            
                replacement_pattern = re.escape(match[0])
                replacement_text = _tex(_type, match[1])
                text = re.sub(replacement_pattern, replacement_text, text)
            elif len(match) == 3:
                if _type == "href":
                    replacement_pattern = re.escape(match[0])
                    url_part, text_part = match[1], match[2]
                    replacement_text = rf"\\href{{{url_part}}}{{{text_part}}}"
                    text = re.sub(replacement_pattern, replacement_text, text)
                elif _type == "heading":
                    replacement_pattern = re.escape(match[0])
                    hashes, text_part = match[1], match[2]
                    heading_level = _get_heading_level(hashes)
                    replacement_text = rf"{heading_level}{{{text_part}}}"
                    text = re.sub(replacement_pattern, replacement_text, text)
        return text

    text = _sub_pattern_to_tex(heading_pattern, "heading", text)
    text = _sub_pattern_to_tex(url_pattern, "href", text)
    text = _sub_pattern_to_tex(inline_code_pattern, "inline_code", text)
    text = _sub_pattern_to_tex(bold_pattern, "bold", text)
    text = _sub_pattern_to_tex(italic_pattern, "italic", text)

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

    # the combined pattern split into paragraph, ordered, and unordered lists 
    # and code block and then we detect individual blocks using appropriate regex
    combined_pattern = re.compile(r"""^\s*(```[\s\S]*?```)$|^(\d+\.\s.*(?:\n*\d+\.\s.*)*)|^(-\s.*(?:\n*-\s.*)*)""", re.M)

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

            # code pattern and code blocks are special because they don't need any processing
            if re.search(code_pattern, split):
                code_block = re.findall(code_pattern, split)[0]
                code_text = code_block
                text = clean_text(code_text)
                text = f"\\begin{{lstlisting}}[breaklines=true, breakatwhitespace=false]\n\n{text}\n\n\\end{{lstlisting}}"
            else:
                if re.search(ul_pattern, split):
                    item_pattern = re.compile(r"""^(?:-\s*(.*)\n*)""", re.M)
                    items = re.findall(item_pattern, split)
                    if items:
                        text = process_list(items, ordered=False)
                elif re.search(ol_pattern, split):
                    item_pattern = re.compile(r"""^(?:\d+\.\s*(.*)\n*)""", re.M)
                    items = re.findall(item_pattern, split)
                    if items:
                        text = process_list(items, ordered=True)

                text = clean_text(split)
                """
                 we are at a fork which to apply first processing inline or escape because process_inline_text will add backslash that escape_latex will try to escape and I cannot use escape_latex first because that will mess up href if present and have characters that need not be escaped. Solution is to not add escape what has already been escaped and then not to escape anything in the url portion of the href  
                """
                text = process_inline_text(text)
                text = escape_latex_text(text)

            if text: # append if not empty
                tex_elements.append(text)

        tex = "\n".join(tex_elements)

        if i % 2 == 0: # even response are users
            tex = '\n\n'.join(tex.split('\n')) # this is a very bad fix to the overflow problem that is caused in tex
            processed_block = f"\\begin{{userprompt}}\n\n{tex}\n\n\\end{{userprompt}}"
        else:
            processed_block = f"\\begin{{botresponse}}\n\n{tex}\n\n\\end{{botresponse}}"
        
        processed_blocks.append(processed_block)

    latex = "\n\n".join(processed_blocks) # I need one blank line between the div elements in the latex format
    
    with open('assorted.tex', 'w', encoding='utf8') as w:
        for line in latex:
            w.write(line)

    # with open('md_to_html_op.txt', 'w', encoding='utf8') as w:
    #     for line in ol_elements:
    #         w.write(line + '\n\n-----------------------------------------\n\n')
    # splits = re.split(code_pattern, markdown_text, flags=re.MULTILINE)    
    # html = markdown.markdown(markdown_text, extensions=['fenced_code'])
    # with open('assorted_1.html', 'w', encoding='utf8') as wp:
    #     wp.write(html)
