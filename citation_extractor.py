#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build two files from in-text citations + Zotero CSV:

• citations.md   – unchanged style: **¹,²,³** with Unicode superscript digits
• citations.html – web/Slides style: <sup><strong>1,2,3</strong></sup>
"""

import re, unicodedata, os, sys
from pathlib import Path

import pandas as pd
import markdown

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

# original Unicode superscript digits for the Markdown file
_super_map = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

def to_superscript(nums):
    """Unicode superscript digits (commas stay normal)."""
    return ','.join(''.join(str(n).translate(_super_map)) for n in nums)

def supers_html(nums):
    """Bold superscripts for HTML – digits *and* commas."""
    return f"<sup><strong>{','.join(str(n) for n in nums)}</strong></sup>"

def normalize_name(name):
    if pd.isna(name):
        return ""
    s = str(name).lower().strip()
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')
    s = re.sub(r'[^\w\s]', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def normalize_author(author_field):
    if pd.isna(author_field):
        return ""
    text = str(author_field)
    if ',' not in text:
        return normalize_name(text)
    first = text.split(';')[0]
    return normalize_name(first.split(',')[0])

def format_apa_authors(author_field):
    if pd.isna(author_field):
        return ""
    parts = [a.strip() for a in str(author_field).split(';')]
    out = []
    for a in parts:
        if ',' in a:
            last, first = a.split(',', 1)
            initials = ' '.join(f"{n[0]}." for n in first.split())
            out.append(f"{last.strip()}, {initials}")
        else:
            out.append(a)
    if len(out) == 1:
        return out[0]
    if len(out) == 2:
        return f"{out[0]} & {out[1]}"
    return f"{', '.join(out[:-1])}, & {out[-1]}"

# ------------------------------------------------------------
# Core routine
# ------------------------------------------------------------

def extract_citations_and_merge_zotero(text_file, zotero_csv, output_md):
    # ---------- read draft ------------------------------------------------
    draft = Path(text_file).read_text(encoding="utf-8")

    # grab all "(Author, 2024)"-style chunks in order of appearance
    raw_groups = re.findall(r'\(([^()]+?)\)', draft)
    in_text_citations = []
    for grp in raw_groups:
        for part in re.split(r';\s*', grp):
            # (Author, Year) or (Author et al., Year) or (Author & Author, Year) i.e., must have comma
            # m = re.match(r'(.+?),\s*(\d{4})$', part.strip())
            # (Author Year) or (Author et al. Year) or (Author & Author Year) i.e., no comma
            m = re.match(r'(.+?)(?:,\s*|\s+)(\d{4})$', part.strip())
            if m:
                in_text_citations.append((m.group(1).strip(), m.group(2)))

    # positions of each citation instance (1-based index)
    cites_by_pair = {}
    for idx, (auth, yr) in enumerate(in_text_citations, 1):
        cites_by_pair.setdefault((auth, yr), []).append(idx)

    # ---------- load Zotero CSV ------------------------------------------
    z = pd.read_csv(zotero_csv, encoding="utf-8")
    z['NormAuthor'] = z['Author'].apply(normalize_author)
    z['Year']       = z['Publication Year'].astype(str).str.extract(r'(\d{4})')
    z['DateAdded']  = pd.to_datetime(z['Date Added'], errors='coerce')

    lookup = {}
    for _, row in z.iterrows():
        lookup.setdefault((row['NormAuthor'], row['Year']), []).append(row)
    for key in lookup:
        lookup[key].sort(key=lambda r: r['DateAdded'])

    # ---------- build two parallel output lists --------------------------
    outputs_md, outputs_html = [], []
    use_counter = {}

    for (raw_auth, yr), pos_list in sorted(cites_by_pair.items(), key=lambda x: x[1][0]):

        norm_raw = normalize_name(raw_auth)
        m_etal   = re.match(r'(.+?)\s+et al\.?', raw_auth, flags=re.I)
        simp     = normalize_name(m_etal.group(1) if m_etal else
                                  raw_auth.split('&')[0] if '&' in raw_auth else
                                  raw_auth)

        keys = ((norm_raw, yr), (simp, yr))
        cand  = None
        for k in keys:
            if k in lookup:
                cand, key_use = lookup[k], k
                break
        if cand is None:
            for (a, y), rows in lookup.items():
                if y == yr and (simp in a or a in simp):
                    cand, key_use = rows, (a, y)
                    break

        # choose how many lines to emit ----------------------------------
        if not cand:      # ------- NOT FOUND
            sup_md, sup_ht = f"**{to_superscript(pos_list)}**", supers_html(pos_list)
            line_md  = f"{sup_md} {raw_auth}, {yr} — NOT FOUND"
            line_htm = f"{sup_ht} {raw_auth}, {yr} — NOT FOUND"
            outputs_md.append(line_md)
            outputs_html.append(line_htm)
        elif len(cand) == 1:  # ---- single Zotero match
            item = cand[0]
            sup_md, sup_ht = f"**{to_superscript(pos_list)}**", supers_html(pos_list)
            apa   = format_apa_authors(item['Author'])
            title = item['Title']
            url   = item.get('Url', '')
            url_part = f" <{url}>" if url else ""
            line_md  = f"{sup_md} {apa} ({yr}). *{title}*.{url_part}"
            line_htm = f"{sup_ht} {apa} ({yr}). <em>{title}</em>.{url_part}"
            outputs_md.append(line_md)
            outputs_html.append(line_htm)
        else:                 # ---- multiple matches: emit per appearance
            for pos in pos_list:
                count = use_counter.get(key_use, 0)
                item  = cand[count] if count < len(cand) else cand[-1]
                use_counter[key_use] = count + 1

                sup_md, sup_ht = f"**{to_superscript([pos])}**", supers_html([pos])
                apa   = format_apa_authors(item['Author'])
                title = item['Title']
                url   = item.get('Url', '')
                url_part = f" <{url}>" if url else ""
                line_md  = f"{sup_md} {apa} ({yr}). *{title}*.{url_part}"
                line_htm = f"{sup_ht} {apa} ({yr}). <em>{title}</em>.{url_part}"
                outputs_md.append(line_md)
                outputs_html.append(line_htm)

    # ---------- write Markdown (unchanged style) -------------------------
    md_text = "\n".join(outputs_md)
    Path(output_md).write_text(md_text, encoding="utf-8")

    # ---------- write HTML (paragraph per citation) ----------------------
    html_body = "\n\n".join(outputs_html)          # blank line ⇒ <p>…</p>
    html_file = Path(output_md).with_suffix(".html")
    html_text = markdown.markdown(
        html_body,
        extensions=["fenced_code", "tables"],
        output_format="html5",
    )
    html_file.write_text(html_text, encoding="utf-8")

    print("✓ Markdown written →", output_md)
    print("✓ HTML written     →", html_file)

# ------------------------------------------------------------
# Entry-point
# ------------------------------------------------------------

if __name__ == "__main__":
    # run from the script’s own folder so relative paths work
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    extract_citations_and_merge_zotero(
        text_file  = "draft.txt",    # ← change if needed
        zotero_csv = "zotero.csv",   # ← change if needed
        output_md  = "citations.md", # final Markdown filename
    )