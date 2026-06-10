import re
import shutil

import mistune
from pathlib import Path

# --- Artikelliste aus TOC.md laden

def load_toc(path="TOC.md"):
    entries = []
    for line in Path(path).read_text().splitlines():
        m = re.match(r'\s*-\s*\[(.+?)\]\((.+?\.md)\)', line)
        if m:
            entries.append((m.group(1), m.group(2)))
    return entries

ARTICLES = load_toc()

# --- Sidebar-HTML generieren

def build_sidebar(articles, current_filename):
    items = []
    for title, filename in articles:
        html_name = filename.replace(".md", ".html")
        cls = ' class="active"' if filename == current_filename else ''
        items.append(f'<li><a href="{html_name}"{cls}>{title}</a></li>')
    return f'<nav><ul>{"".join(items)}</ul></nav>'

TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
   <meta charset="utf-8">
   <meta name="viewport" content="width=device-width, initial-scale=1">
   <title>{{TITLE}}</title>
   <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="layout">
  <aside class="sidebar">{{SIDEBAR}}</aside>
  <main class="content">{{CONTENT}}</main>
</div>
</body>
</html>
"""

# Configure the converter: allow raw HTML through, enable table syntax
renderer = mistune.create_markdown(escape=False, plugins=["table", "strikethrough"])

# Fix links from md to html
def fix_internal_links(html, articles):
    """Biegt Links von .md auf .html um, für jeden bekannten Artikel."""
    for _, filename in articles:
        html_name = filename.replace(".md", ".html")
        html = html.replace(f'href="{filename}"', f'href="{html_name}"')
    return html

# Ausgabeordner anlegen, falls noch nicht vorhanden
docs = Path("docs")
docs.mkdir(exist_ok=True)
shutil.copy("style.css", docs / "style.css")

# Schleife um Artikel zu bauen
for title, filename in ARTICLES:
    with open(Path("articles", filename)) as f:
        md = f.read()
    content_html = renderer(md)
    content_html = fix_internal_links(content_html, ARTICLES)
    sidebar_html = build_sidebar(ARTICLES, filename)
    page = TEMPLATE.replace("{{TITLE}}", title) \
                   .replace("{{SIDEBAR}}", sidebar_html) \
                   .replace("{{CONTENT}}", content_html)
    out_name = filename.replace(".md", ".html")
    with open(docs / out_name, "w") as f:
        f.write(page)
    print(f" docs/{out_name}")

print(f"Fertig: {len(ARTICLES)} Seiten in docs/")
