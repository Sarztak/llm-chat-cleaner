import re

text = """
- a
- b
- c

x
y
- m
- n
- k
"""
def main():
    pattern = r"""^(?:-\s.*(?:\n*-\s.*)*)+"""
    splits = re.split(pattern, text, flags=re.MULTILINE)
    matches = re.findall(pattern, text, re.MULTILINE)
    breakpoint()

if __name__ == "__main__":
    main()