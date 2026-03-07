# the main purpose of this code is to remove unwanted tags from the html version of an chat from claude. But it is not useful to do so since everything works fine even without cleaning other tags
import json
import sys
import re
from lxml import html
from lxml.etree import _Element, _ElementTree
from typing import cast # cast to satisfy the type checker

# parse the file directly given the file path as first argument
doc: _ElementTree = html.parse(sys.argv[1])

# extract the date on which chat was created
# pattern to extract date need to add str data type to silence pylance
date_pattern: re.Pattern[str] = re.compile(r'created_at\":\"(.*?)\"') 
doc_string: str = cast(str, html.tostring(doc, encoding='unicode')) # convert to string
match: re.Match[str] | None = re.search(
    date_pattern, doc_string, flags=re.MULTILINE | re.DOTALL
)

if match:
    created_at = match.group(1).strip()

# 1. throw away every <svg>, <img>, <button> and their content
tag: _Element
for tag in doc.xpath('//svg | //img | //button | //style | //script'):
    tag.getparent().remove(tag)

# 2. collect the cleaned assistant blocks
out: list[dict[str, str]] = []
html_content: list[str] = []
div: _Element
for div in doc.xpath('//div[@data-testid="user-message"] | //div[starts-with(@class,"font-claude-response")]'):
    role = 'user' if div.get('data-testid') else 'assistant'

    # strip ALL attributes except href on <a>
    el: _Element
    for el in div.iter():
        if el.tag == 'a':
            href: str | None = el.get('href')
            el.attrib.clear()
            if href:
                el.set('href', href)
        else:
            el.attrib.clear()

    # strip unsupported tags but keep their text
    unsupported: set[str] = {'span', 'div', 'section', 'article', 'nav', 'header', 'footer'}
    for tag in div.xpath('.//*'):
        if tag.tag in unsupported:
            # unwrap: remove tag, keep text
            tag.drop_tag()

    turn: str = cast(str, html.tostring(div, encoding='unicode').strip())
    html_role_appened: str = f"<div><strong>{role}:</strong><br>{turn}</div><hr>"
    out.append({'role': role, 'html': html_role_appened})
    html_content.append(html_role_appened)

# Write to HTML file
with open('conversation2.html', 'w', encoding='utf8') as f:
    f.write('\n'.join(html_content))
    json.dump(out, f, ensure_ascii=False, indent=2)
