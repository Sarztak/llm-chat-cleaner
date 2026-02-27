from md_to_html import process_blocks
from pathlib import Path


def main():
    md_dir = Path("./markdown/")
    md_to_tex_out_dir = Path("./md_to_tex")
    md_to_tex_out_dir.mkdir(exist_ok=True, parents=True)

    for path in md_dir.iterdir():
        print(path.stem)
        with open(path, "r", encoding="utf-8-sig") as fp:
            content = fp.read()
        with open(path, "w", encoding="utf8") as fp:
            fp.write(content) # this needs to be done because there is a Byte Order Mark \ufeff in the beginning of each file

        with open(path, "r", encoding="utf8") as fp:
            chat_text = fp.read()

        if not chat_text.startswith('User prompt'):
            continue

        processed_chat = process_blocks(chat_text=chat_text)
        md_to_tex = "\n\n".join(processed_chat)

        with open(md_to_tex_out_dir / f"{path.stem}.tex", "w", encoding="utf8") as w:
            for line in md_to_tex:
                w.write(line)

if __name__ == "__main__":
    main()
