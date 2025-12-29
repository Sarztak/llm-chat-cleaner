import json
from markdownify import markdownify as md

# read json
with open('stripped.json', encoding='utf8') as f:
    turns = json.load(f)

# convert to markdown
output = []
for turn in turns:
    role = "**User:**" if turn['role'] == 'user' else "**Claude:**"
    # timestamp = turn['created_at']
    html = turn['html']
    
    # convert html to markdown
    markdown_text = md(html)
    
    output.append(f"{role}\n\n{markdown_text}\n")

# write to file
with open('chat.md', 'w', encoding='utf8') as f:
    f.write('\n---\n\n'.join(output))

print('chat.md written')