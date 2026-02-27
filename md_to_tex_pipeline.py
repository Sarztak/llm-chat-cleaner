from md_to_html import process_blocks
from pathlib import Path
import shutil
import subprocess
import os
import time

main_tex_template = r"""
\documentclass[11pt,a4paper]{{book}}
% Include all package imports and settings
\input{{preamble}}
% Include custom environment definitions
\input{{environments}}
\begin{{document}}
% Include conversation files
\input{{"{}"}}
\end{{document}}
"""


def main():
    md_dir = Path("./markdown/")
    md_to_tex_out_dir = Path("./md_to_tex")
    md_to_tex_out_dir.mkdir(exist_ok=True, parents=True)

    for path in md_dir.iterdir():
        print(path.stem)
        with open(path, "r", encoding="utf-8-sig") as fp:
            content = fp.read()
        with open(path, "w", encoding="utf8") as fp:
            fp.write(
                content
            )  # this needs to be done because there is a Byte Order Mark \ufeff in the beginning of each file

        with open(path, "r", encoding="utf8") as fp:
            chat_text = fp.read()

        if not chat_text.startswith("User prompt"):
            continue

        processed_chat = process_blocks(chat_text=chat_text)
        md_to_tex = "\n\n".join(processed_chat)

        with open(md_to_tex_out_dir / f"{path.stem}.tex", "w", encoding="utf8") as w:
            for line in md_to_tex:
                w.write(line)


def tex_to_pdf():
    cwd = Path.cwd()
    md_to_tex_out_dir = Path("./md_to_tex")
    tex_to_pdf_dir = Path("./tex_to_pdf")
    tex_to_pdf_dir.mkdir(exist_ok=True, parents=True)
    main_tex_path = cwd / "pdf_latex/main.tex"
    for path in md_to_tex_out_dir.iterdir():
        with open(main_tex_path, "w", encoding="utf8") as w:
            tex_path = str(cwd / path)
            tex_path = tex_path.replace(
                "\\", "/"
            )  # latex can handle windows path with forward slash
            w.write(main_tex_template.format(tex_path))
        os.chdir(cwd / "pdf_latex")
        result = subprocess.Popen(
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = result.communicate()  # This blocks until the process finishes
        os.chdir(cwd)
        shutil.copy(cwd / "pdf_latex/main.pdf", tex_to_pdf_dir / f"{path.stem}.pdf")


if __name__ == "__main__":
    # main()
    tex_to_pdf()
