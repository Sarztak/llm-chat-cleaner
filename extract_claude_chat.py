import json, sys, re
from lxml import html as lh

doc = lh.parse(sys.argv[1])

date_pattern = r"""created_at\\":\\"(.*?)\\"""
doc_string = lh.tostring(doc, encoding='unicode') 
created_at = re.search(date_pattern, doc_string, flags=re.MULTILINE | re.DOTALL).group(1).strip()

out = []
for div in doc.xpath('//div[@data-testid="user-message"] | //div[starts-with(@class,"font-claude-message")]'):
    role = 'user' if div.get('data-testid') else 'assistant'
    out.append({'role': role, 'html': lh.tostring(div, encoding='unicode').strip(), 'created_at': created_at})

with open('chat.jsonl', 'w', encoding='utf8') as f:
    for turn in out:
        f.write(json.dumps(turn, ensure_ascii=False) + '\n')

print('Done:', len(out), 'turns → chat.jsonl')