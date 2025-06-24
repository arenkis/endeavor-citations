````md
# Citation Pipeline – *From APA in-text citations to web-ready superscripts*

A tiny three-part tool-chain that turns the usual “(Author, 2025)” calls in your draft into clean numeric superscripts, ready for print **and** Google Slides.

| Script / Notebook              | Role                                                                                                                                                                                                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`citation_extractor.py`**    | Parses a plain-text draft, cross-references it with a Zotero CSV export, and emits two reference lists: <br>• **`citations.md`** – Unicode superscript digits for print/PDF <br>• **`citations.html`** – `<sup><strong>…</strong></sup>` for the web & Google Slides |
| **`citation_extractor.ipynb`** | *Zero-install route.* A self-contained Google Colab notebook (Spanish UI) that walks you through uploading `draft.txt` + `zotero.csv`, then auto-downloads **`citations.md`** and **`citations.html`** in one click.                                                      |
| **`citation_replacer.gs`**     | A Google Apps Script that adds **Citations → Replace All** to Slides. It converts every APA-style citation (comma **or** whitespace-only, with optional chains) into properly numbered superscripts that match the extractor’s list.                                       |

---

## 1 · Why you might want this

* **One-click references.** Keep drafting in APA. When you’re ready to publish:

  1. run the Python script *or* the Colab notebook,
  2. click **Replace All** in Slides,
  3. paste the HTML list onto a *References* slide (or under your article).

* **Stable numbering.** Citations are numbered strictly by first appearance, so edits won’t reshuffle anything.

* **Built-in sanity checks.** Any citation that can’t be matched to Zotero is flagged with **“— NOT FOUND”**.

---

## 2 · Quick start

<details>
<summary><strong>2.0  No-install route – Google Colab (recommended for occasional users)</strong></summary>

1. **Open the notebook** → <https://colab.research.google.com/github/endeavor-citations/citation_extractor.ipynb>  
   (or click the “Open in Colab” badge in this repo).

2. Click **Runtime → Run all**.  
   When prompted, upload **`draft.txt`** and **`zotero.csv`**.

3. Wait ⏱ 15-30 s. Colab will:

   * clean the workspace,  
   * generate **`citations.md`** & **`citations.html`**,  
   * trigger both downloads automatically.

4. Drop the HTML list onto your *References* slide, then run **Citations → Replace All** in Slides.

¡Eso es todo!
</details>

### 2.1 Prepare your folder (local workflow)

```text
project/
├─ citation_extractor.py
├─ citation_extractor.ipynb   # optional – Colab version
├─ citation_replacer.gs
├─ draft.txt                  # your manuscript – plain text
└─ zotero.csv                 # “CSV” export from Zotero
````

> **Draft source**
> • **Google Docs:** **File → Download → Plain text (.txt)** → save as `draft.txt`.
> • Any editor works—just ensure UTF-8 and keep the filename.

### 2.2 Install the Python requirements

```bash
python -m pip install pandas markdown
```

*(Python ≥ 3.8 recommended)*

### 2.3 Generate the reference list

```bash
python citation_extractor.py
# or specify paths:
python citation_extractor.py path/to/draft.txt path/to/zotero.csv output.md
```

Expected output:

```
✓ Markdown written → citations.md
✓ HTML written     → citations.html
```

### 2.4 Wire up Google Slides

1. Open your deck → **Extensions → Apps Script**
2. Replace the default code with **`citation_replacer.gs`** → **Save**
3. Reload Slides (to load the new menu)
4. **Citations → Replace All** → grant the one-time permissions → done

All in-text citations are now neat superscripts. Punctuation and spacing are preserved.

---

## 3 · Workflow in a nutshell

1. **Write** as usual: “According to Smith (2025)…; see also Brown & Lee 2024”.
2. **Export** your Zotero library (or collection) as CSV → `zotero.csv`.
3. **Run** the extractor (script or Colab) → `citations.(md|html)`.
4. **Replace** citations in Slides.
5. **Drop** the HTML list onto a *References* slide.

---

## 4 · Customisation

| Need                                     | How to do it                                                                                                                |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Different file names**                 | Edit the three variables at the bottom of `citation_extractor.py`, or call `extract_citations_and_merge_zotero()` directly. |
| **Change numbering glyphs**              | Tweak the helpers at the top of `citation_extractor.py`: `to_superscript()` (Markdown) and `supers_html()` (HTML).          |
| **Run on Google Docs instead of Slides** | The Apps Script logic is slide-specific. Port to Docs by iterating over `Body.getText()` instead of slide elements.         |

---

## 5 · Troubleshooting

| Symptom / message                          | Likely cause → fix                                                                                                                      |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| **“— NOT FOUND”** in the list              | Author/year pair wasn’t found in `zotero.csv`. Check spelling—the first author in Zotero must match the in-text name.                   |
| Numbers skip (e.g. 1, 3, 4 …)              | You ran **Replace All** twice. Undo once or reload the deck before running it again.                                                    |
| Apps Script asks for “unsafe” permissions  | It only needs the active presentation and logging. Google shows a generic warning for all custom scripts—click **Advanced → Continue**. |
| Colab says “Debes subir UN .txt y UN .csv” | You uploaded the wrong number of files. Upload exactly one `.txt` and one `.csv`.                                                       |
| `UnicodeDecodeError` when reading the TXT  | Draft isn’t UTF-8. Re-export from Docs/Word choosing UTF-8.                                                                             |
| Browser blocks the downloads               | Chrome sometimes blocks multiple downloads. Look for a yellow bar or icon near the URL → **Allow**.                                     |

---

## 6 · Project structure

```text
.
├─ citation_extractor.py       # Python – extract, merge, write
├─ citation_extractor.ipynb    # Colab notebook – browser workflow
├─ citation_replacer.gs        # Apps Script – in-deck superscripts
├─ draft.txt                   # Your manuscript
├─ zotero.csv                  # Zotero export
├─ citations.md                # Output – print/PDF
└─ citations.html              # Output – web/Slides
```

---

## 7 · License

MIT License