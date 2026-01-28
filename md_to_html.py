import markdown
import re

if __name__ == "__main__":
    with open('assorted 1.md', 'r', encoding='utf8') as fp:
        lines = fp.readlines()
    markdown_text = "".join(lines)
    code_pattern = r"""^\s*```([\s\S]*?)```$"""
    ol_pattern = r"""^(\d+\.\s.*(?:\n*\d+\.\s.*)*)"""
    ul_pattern = r"""^(-\s.*(?:\n*-\s.*)*)*"""
    splits = re.split(code_pattern, markdown_text, flags=re.MULTILINE)    
    breakpoint()
    # html = markdown.markdown(markdown_text, extensions=['fenced_code'])
    # with open('assorted_1.html', 'w', encoding='utf8') as wp:
    #     wp.write(html)