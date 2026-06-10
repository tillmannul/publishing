# Projekt: Publishing

Statischer Site-Generator. `build.py` wandelt Markdown aus `articles/`
in HTML nach `docs/` um. Vorbild: aiaiai.guide.

## Architektur
- Artikel-Auswahl und Reihenfolge: `toc.md`, nicht hartkodiert.
- `build.py` liest `toc.md`, rendert mit mistune, wendet ein HTML-Template
  und `style.css` an, schreibt nach `docs/`.
- Interne Links in Markdown auf `.md` zeigen lassen; der Build biegt sie
  auf `.html` um (`fix_internal_links`).
- `docs/` wird bei jedem Build gelöscht und neu erzeugt.

## Konventionen
- `docs/` ist reines Build-Ergebnis. Nie von Hand editieren.
- `.venv/` ist die virtuelle Umgebung. Nicht anfassen, nicht committen.
- Sprache der Inhalte: Deutsch.

## Arbeitsweise mit Claude Code
- Immer zuerst im Plan-Modus erklären, welche Dateien wie geändert werden
  und warum. Nichts ohne Freigabe ändern.
- Verständlich erklären, der Autor lernt gerade Programmieren.
- Lösungen einfach und nachvollziehbar halten, kein unnötiger Abstraktions-Overhead.