import shutil

import mistune
from pathlib import Path

# --- Welche Artikel werden gebaut?

ARTICLES = [
    ("Building in Public, Quietly", "helloworld.md"),
    ("Notizen zum Generator", "generator.md"),
    ("Hilfreiche Shortcuts", "shortcuts.md")
]

TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
   <meta charset="utf-8">
   <meta name="viewport" content="width=device-width, initial-scale=1">
   <title>{{TITLE}}</title>
   <link rel="stylesheet" href="style.css">
</head>
<body>
{{CONTENT}}
</body>
</html>
"""

# Configure the converter: allow raw HTML through, enable tyble syntax
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
    page = TEMPLATE.replace("{{TITLE}}", title) \
                    .replace("{{CONTENT}}", content_html)
    out_name = filename.replace(".md", ".html")
    with open(docs / out_name, "w") as f:
        f.write(page)
    print (f" docs/{out_name}")

print(f"Fertig: {len(ARTICLES)} Seiten in docs/")

