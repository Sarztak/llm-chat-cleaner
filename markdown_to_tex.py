import re
import markdown
# open the file first
user_pattern = 'User prompt'
bot_pattern = 'GPT-4o mini'
pattern = rf'{user_pattern}|{bot_pattern}'
paragraphs = dict(user=[], bot=[])

def collect_line(fp, role):
    para = []
    while True:
        # read current line and move pointer to the beginning of next line
        current_line = fp.readline()
        match = re.search(pattern, current_line)
        if not current_line or match: # if current_line is user/bot message start
            fp.seek(fp.tell() - len(current_line)) # reset the pointer back to beginning of the line
            paragraphs[role].append(para)
            break
        para.append(current_line) # current line if not user/bot then store


with open('assorted 1.md', 'r', encoding='utf8') as fp:
    while True:
        line = fp.readline() # this will move the pointer to the next line
        if not line:
            break
        # start or stop
        match = re.search(pattern, line) # I expect file to start with user
        if match:
            if match.group() == user_pattern:
                collect_line(fp, 'user')
            elif match.group() == bot_pattern:
                collect_line(fp, 'bot')

if __name__ == "__main__":
    with open('assorted 1.md', 'r', encoding='utf8') as fp:
        lines = fp.readlines()
    breakpoint()
    markdown_text = "".join(lines)
    html = markdown.markdown(markdown_text, extensions=['fenced_code', 'codehilite'])
    with open('assorted_1.html', 'w', encoding='utf8') as wp:
        wp.write(html)