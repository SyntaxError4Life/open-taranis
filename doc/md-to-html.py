import os
from pathlib import Path
from markdown_it import MarkdownIt

LANGS = ["fr", "en"]

from markdown_it import MarkdownIt
import re

def md_to_html(md_content: str) -> str:
    md = MarkdownIt()
    html = md.render(md_content)
    
    # Ajoute <br> entre les paragraphes consécutifs
    html = re.sub(r'</p>\s*\n\s*<p>', '</p>\n<br>\n<p>', html)
    
    # Ajoute <br> autour du <hr />
    html = re.sub(r'<hr\s*/?>', '<br>\n<hr/>\n<br>', html)
    
    # Ajoute <br> après les blocs de code </pre>
    html = re.sub(r'</pre>', '</pre>\n<br>', html)
    
    return html

def process_language(lang: str):
    base_path = Path("doc") / lang
    source_dir = base_path / "content-source"
    output_dir = base_path / "content"
    
    if not source_dir.exists():
        print(f"[{lang}] content-source/ introuvable")
        return
    
    md_files = list(source_dir.rglob("*.md"))
    
    for md_file in md_files:
        relative_path = md_file.relative_to(source_dir)
        html_file = output_dir / relative_path.with_suffix(".html")
        
        html_file.parent.mkdir(parents=True, exist_ok=True)
        
        md_content = md_file.read_text(encoding="utf-8")
        html_content = md_to_html(md_content)
        html_file.write_text(html_content, encoding="utf-8")

def main():
    for lang in LANGS:
        process_language(lang)
    print("Conversion terminée")

if __name__ == "__main__":
    main()