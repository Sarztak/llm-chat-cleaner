import re
from collections import deque

# would splitting by capture group be a better idea ? 
def capture_code_blocks(text):
    pattern = r"""^`{3}(.*?)`{3}$"""
    matches = re.findall(pattern, text, re.MULTILINE|re.DOTALL)

def capture_ordered_list(text):
    pattern = r"""^(\d+\.\s.*(?:\n*\d+\.\s.*)*)"""
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
    pattern = r"""^(-\s.*(?:\n*-\s.*)*)*"""
    matches = re.findall(pattern, text, re.MULTILINE)

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


if __name__ == "__main__":
    # open the file first
    user_pattern = 'User prompt'
    bot_pattern = 'GPT-4o mini'
    pattern = rf'{user_pattern}|{bot_pattern}'
    paragraphs = dict(user=[], bot=[])

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
