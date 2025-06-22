# Citation Pipeline – *From APA in-text citations to web-ready superscripts*

This project is a tiny two-part tool-chain:

| Script                      | Role                                                                                                                                                                                                                                                               |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`citation_extractor.py`** | Parses a plain-text draft, cross-references it with a Zotero CSV export, and emits two reference lists:<br>• **`citations.md`** – Unicode superscript digits for print/PDF<br>• **`citations.html`** – `<sup><strong>…</strong></sup>` for the web & Google Slides |
| **`citation_replacer.gs`**  | A Google Apps Script that adds **Citations → Replace All** to Slides. It converts every “(Author, 2024)” (with optional “; …” chains) into properly styled numeric superscripts that match the list created by the Python script.                                  |

---

## 1 · Why you might want this

* **One-click references.** Keep writing in APA style while drafting. When you’re ready to present or publish:

  1. run the Python script → get a clean numeric reference list,
  2. click *Replace All* in Slides → swap the in-text calls for neat superscripts,
  3. paste the HTML list onto a *References* slide (or under your article).

* **Stable numbering.** Citations are numbered strictly by first appearance, so every superscript always points to the same entry—even after edits.

* **Built-in sanity checks.** Any citation that can’t be matched in the Zotero export is flagged with **“— NOT FOUND”** so nothing slips through.

---

## 2 · Quick start

### 2.1 Prepare your folder

```
project/
├─ citation_extractor.py
├─ citation_replacer.gs
├─ draft.txt           # your manuscript – plain text
└─ zotero.csv          # “CSV” export from Zotero
```

> **Draft source**
> • **Google Workspace:** choose **File → Download → Plain text (.txt)** and save as `draft.txt` in this folder.
> • Any other editor works too—just make sure the file is UTF-8 and that the file name matches what the script expects (default: `draft.txt`).

### 2.2 Install the Python requirements

```bash
python -m pip install pandas markdown
```

*(Python 3.8 + recommended)*

### 2.3 Generate the reference list

```bash
python citation_extractor.py
# or specify paths manually:
python citation_extractor.py path/to/draft.txt path/to/zotero.csv output.md
```

The script prints:

```
✓ Markdown written → citations.md
✓ HTML written     → citations.html
```

### 2.4 Wire up Google Slides

1. Open your slide deck → **Extensions → Apps Script**
2. Replace the default code with the contents of **`citation_replacer.gs`** and **save**
3. Reload the deck (Slides needs to load the new menu)
4. **Citations → Replace All** → grant the one-time permissions → done

Every in-text APA call is now a numeric superscript. Punctuation is preserved, dangling spaces are cleaned automatically.

---

## 3 · Workflow in a nutshell

1. **Write** as usual: “According to Smith (2023)…; see also Brown & Lee (2022)”
2. **Export** your Zotero library (or a collection) as CSV → `zotero.csv`
3. **Run** `citation_extractor.py` → `citations.(md|html)`
4. **Replace** citations in Slides (menu → Replace All)
5. **Drop** the HTML list onto a *References* slide (Slides keeps the `<sup>` styling)

---

## 4 · Customisation

| Need                                     | How to do it                                                                                                                        |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Different file names**                 | Edit the three variables at the bottom of `citation_extractor.py`, or call `extract_citations_and_merge_zotero()` directly.         |
| **Change numbering glyphs**              | Tweak the helpers at the top of `citation_extractor.py`: `to_superscript()` (Markdown) and `supers_html()` (HTML).                  |
| **Run on Google Docs instead of Slides** | The Apps Script logic is slide-specific (text shapes & element walk). Porting it to Docs is possible—iterate over `Body.getText()`. |

---

## 5 · Troubleshooting

| Symptom                               | Likely cause & fix                                                                                                                                      |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **“— NOT FOUND”** in the list         | The author/year pair didn’t match any row in `zotero.csv`. Check spelling and that the first author in Zotero matches the in-text name.                 |
| Numbers skip (e.g. 1, 3, 4…)          | You replaced citations twice. Undo once or reload the deck before running *Replace All* again.                                                          |
| Apps Script asks for more permissions | The script only needs access to the active presentation and logging. Google shows a generic warning for all custom scripts—click *Advanced → Continue*. |

---

## 6 · Project structure

```
.
├─ citation_extractor.py   # Python – extract, merge, write
├─ citation_replacer.gs    # Apps Script – in-deck superscripts
├─ draft.txt               # Your manuscript
├─ zotero.csv              # Zotero export
├─ citations.md            # Output – print/PDF
└─ citations.html          # Output – web/Slides
```

---

## 7 · License

MIT License.