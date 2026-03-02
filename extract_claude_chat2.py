from parse_chat import chat_html_to_latex
from pathlib import Path
from md_to_tex_pipeline import convert_from_tex_to_pdf

def main():
    claude_dir = Path("./claude")
    (claude_dir / "tex").mkdir(exist_ok=True, parents=True)
    (claude_dir / "pdf").mkdir(exist_ok=True, parents=True)
    
    
    for html_file_path in (claude_dir / "html").glob("*.html"):

        with open(html_file_path, "r", encoding="utf8") as fp:
            html = fp.read()
        latex = chat_html_to_latex(html)

        with open(claude_dir / f"tex/{html_file_path.stem}.tex", "w", encoding="utf8") as w:
            w.write(latex)
    convert_from_tex_to_pdf(tex_dir=claude_dir / "tex", pdf_dir=claude_dir / "pdf")
if __name__ == "__main__":
    main()
