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
   <meta name="robots" content="noindex">
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

# Ausgabeordner frisch anlegen
docs = Path("docs")
if docs.exists():
    shutil.rmtree(docs)
docs.mkdir()
shutil.copy("style.css", docs / "style.css")

# Schleife um Artikel zu bauen
already_built = set()
for title, filename in ARTICLES:
    if filename in already_built:
        continue
    already_built.add(filename)
    article_path = Path("articles", filename)
    if not article_path.exists():
        print(f"WARNUNG: '{filename}' in TOC.md gelistet, aber nicht in articles/ gefunden — übersprungen.")
        continue
    with open(article_path) as f:
        md = f.read()
    content_html = renderer(md)
    content_html = fix_internal_links(content_html, ARTICLES)
    content_html += '<footer><hr><a href="main.html">Back to main</a></footer>'
    sidebar_html = build_sidebar(ARTICLES, filename)
    page = TEMPLATE.replace("{{TITLE}}", title) \
                   .replace("{{SIDEBAR}}", sidebar_html) \
                   .replace("{{CONTENT}}", content_html)
    out_name = filename.replace(".md", ".html")
    with open(docs / out_name, "w") as f:
        f.write(page)
    print(f" docs/{out_name}")

# main.html bauen (deduplizierte TOC-Liste als Inhalt)
seen = set()
toc_items = []
for title, filename in ARTICLES:
    if filename in seen:
        continue
    seen.add(filename)
    html_name = filename.replace(".md", ".html")
    toc_items.append(f'<li><a href="{html_name}">{title}</a></li>')

toc_content = f'<h1>Contents</h1><ul>{"".join(toc_items)}</ul>'
sidebar_html = build_sidebar(ARTICLES, None)
main_page = TEMPLATE.replace("{{TITLE}}", "Contents") \
                    .replace("{{SIDEBAR}}", sidebar_html) \
                    .replace("{{CONTENT}}", toc_content)
with open(docs / "main.html", "w") as f:
    f.write(main_page)
print(f" docs/main.html")

print(f"Fertig: {len(ARTICLES)} Seiten in docs/")
