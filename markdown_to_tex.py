import re
from collections import deque
import markdown
# open the file first
user_pattern = 'User prompt'
bot_pattern = 'GPT-4o mini'
pattern = rf'{user_pattern}|{bot_pattern}'
paragraphs = dict(user=[], bot=[])


def capture_ordered_list(text):
    pattern = r"""^(\d+)\.\s(.*)"""
    matches = re.findall(pattern, text, re.MULTILINE)
    queue = deque(matches)
    lists = []
    item_list = []
    if queue: # check if the matches is empty or not
        num, item = queue.popleft() # the first match should be 1. 
        if num == 1:
            item_list.append(item) # add the first match and then start poping
        while queue:
            num, item = queue.popleft()
            if num == 1: # this means we have a new ordered list
                lists.append(item_list) # add to the collection of lists
                item_list = [] # start a new list
                item_list.append(item)
            else:
                item_list.append(item) # add the next item in sequence

    # lists should now contain all the ordered lists

def capture_unordered_list(text):
    pattern = r"""^-\s(.*)"""
    matches = re.findall(pattern, text, re.MULTILINE)

    # now this is going to be trickly because there is no delimiter

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
    markdown_text = "".join(lines)
    html = markdown.markdown(markdown_text, extensions=['fenced_code'])
    with open('assorted_1.html', 'w', encoding='utf8') as wp:
        wp.write(html)