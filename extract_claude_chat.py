import json, sys, re
from lxml import html

# parse the file directly given the file path as first argument
doc = html.parse(sys.argv[1])

# extract the date on which chat was created
date_pattern = r"""created_at\\":\\"(.*?)\\""" # pattern to extract date
doc_string = html.tostring(doc, encoding='unicode') # convert to string
created_at = re.search(
    date_pattern, doc_string, flags=re.MULTILINE | re.DOTALL
).group(1).strip()

# 1. throw away every <svg>, <img>, <button> and their content
for tag in doc.xpath('//svg | //img | //button | //style | //script'):
    tag.getparent().remove(tag)

# 2. keep only the block elements 
# keep = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
#         'ul', 'ol', 'li', 'blockquote', 'pre', 'a'}
# for el in doc.xpath('//*[not(self::{})]'.format(' or self::'.join(keep))):
#     el.drop_tree()          # removes node, keeps text
#     # use el.getparent().remove(el) to ditch text too
# breakpoint()

# 3. collect the cleaned assistant blocks
out, html_content = [], []
for div in doc.xpath('//div[@data-testid="user-message"] | //div[starts-with(@class,"font-claude-message")]'):
    role = 'user' if div.get('data-testid') else 'assistant'

    # strip ALL attributes except href on <a>
    for el in div.iter():
        if el.tag == 'a':
            href = el.get('href')
            el.attrib.clear()
            if href:
                el.set('href', href)
        else:
            el.attrib.clear()

    # strip unsupported tags but keep their text
    unsupported = {'span', 'div', 'section', 'article', 'nav', 'header', 'footer'}
    for tag in div.xpath('.//*'):
        if tag.tag in unsupported:
            # unwrap: remove tag, keep text
            tag.drop_tag()

    turn = html.tostring(div, encoding='unicode').strip()
    html_role_appened = f"<div><strong>{role}:</strong><br>{turn}</div><hr>"
    out.append({'role': role, 'html': html_role_appened})
    html_content.append(html_role_appened)

# Write to HTML file
with open('conversation.html', 'w', encoding='utf8') as f:
    f.write('\n'.join(html_content))

# Write to json file
with open('stripped.json', 'w', encoding='utf8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)