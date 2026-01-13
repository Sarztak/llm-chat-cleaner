from bs4 import BeautifulSoup, NavigableString
from pathlib import Path


def main():
    with open('hyperband.html', 'r', encoding='utf8') as fp:
        html_parser = BeautifulSoup(
            fp, 'html.parser',multi_valued_attributes=None
        )
    
    divs = html_parser.find_all('div')
    for div in divs:
        if div.get('data-testid', "") == 'user-message':
            breakpoint()
            ...
        elif div.get('class', "").startswith('font-claude-message'):
            breakpoint()
            ...

if __name__ == "__main__":
    main()