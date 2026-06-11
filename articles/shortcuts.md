
# Setup

*In project folder:* source .venv/bin/activate

# VI

## Mode-Wechsel
* **`i / a;  esc`**: insert / append.
* **`:w`** : Datei speichern (*write*).
* **`:wq`** : Speichern und `vi` beenden.
* **`:q!`** : Beenden erzwingen, ohne zu speichern.


## Navigation (Command Mode)
* **`h`** / **`j`** / **`k`** / **`l`** : Nach links / unten / oben / rechts bewegen.
* **`5j`** : 5 nach unten.
* **`w`** : Ein Wort nach vorne springen (*word*).
* **`b`** : Ein Wort zurückspringen (*back*).
* **`0` (Null)** : An den absoluten Anfang der aktuellen Zeile springen.
* **`$`** : Ans Ende der aktuellen Zeile springen.
* **`gg`** : Zum Anfang des gesamten Dokuments springen.
* **`G`** : Zum Ende des gesamten Dokuments springen.
* **`L`** / **`M`** / **`H`** : Auf aktuellem Screen Low (ganz runter), Middle, High

## Editieren & Moduswechsel
* **`x`** : Den einzelnen Buchstaben direkt unter dem Cursor löschen.
* **`dw`** : Das aktuelle Wort ab der Cursorposition löschen (*delete word*).
* **`dd`** : Die komplette aktuelle Zeile löschen (und in die Zwischenablage kopieren).
* **`yy`** : Die aktuelle Zeile kopieren (*yank*).
* **`p`** : Kopierten Text oder gelöschte Zeilen nach dem Cursor einfügen (*paste*).
* **`u`** : Die letzte Aktion rückgängig machen (*undo*).
* **`Strg` + `r`** : Die rückgängig gemachte Aktion wiederholen (*redo*).

## Copy and paste
* **`v`** : Aktiviert den **zeichenweisen** Visual Mode. Du markierst ab dem Cursor Buchstabe für Buchstabe.
* **`V` (Shift + v)** : Aktiviert den **zeilenweisen** Visual Mode. Markiert sofort die ganze aktuelle Zeile und jede weitere, zu der du scrollst (perfekt für ganze Abschnitte).
* **`y`** : Kopieren (*yank*) – Kopiert den aktuell markierten Text (im Visual Mode).
* **`d`** : Ausschneiden / Löschen (*delete*) – Schneidet den aktuell markierten Text aus.
* **`p`** : Einfügen (*paste*) – Fügt den kopierten/ausgeschnittenen Text *nach* dem Cursor (oder unter der aktuellen Zeile) ein.
* **`P` (Shift + p)** : Einfügen *vor* dem Cursor (oder über der aktuellen Zeile).
* **`yiw`** : Kopiert das aktuelle Wort, auf dem der Cursor steht (*yank inner word*).
* **`diw`** : Schneidet das aktuelle Wort aus, auf dem der Cursor steht (*delete inner word*).
* **`y$`** : Kopiert alles von der aktuellen Cursorposition bis zum Ende der Zeile.
* **`d$`** : Schneidet alles von der aktuellen Cursorposition bis zum Ende der Zeile aus.

--- 

# VS
* Cmd + Shift + 7 - aus-/einkommentieren


* Cmd + Shift + v - Render Markdown (and switch back)

---

# Git
* git log --oneline
* git diff datei: Änderungen anzeigen
* stage: git add [path]
* commit: git commit -m [comment]
* push to github: git push

* git status


---


# MD

| Syntax | Result |
|---|---|
| `*italic*` or `_italic_` | *italic* |
| `**bold**` | **bold** |
| `***bold italic***` | ***bold italic*** |
| `~~strikethrough~~` | ~~strikethrough~~ |


## Links and Images

| Syntax | Purpose |
|---|---|
| `[text](https://url.com)` | Link |
| `[text](url "tooltip")` | Link with hover title |
| `![alt text](image.png)` | Image |
| `<https://url.com>` | Auto-link |

## Code

**Inline:** `` `code` `` → `code`

**Block** (specify language for highlighting):
````
```python
print("hello")
```
````

## Blockquote

```
> Quoted text
>> Nested quote
```

## Tables

```
| Left | Center | Right |
|:-----|:------:|------:|
| a    | b      | c     |
```
Colons in the separator row set alignment.


