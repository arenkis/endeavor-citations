/**
 * Google Slides helper
 * Menu → Citations → Replace All
 * Turns “(Author, 2024)” into “.1” or “,1,2” with proper superscript styling.
 */

function onOpen() {
  SlidesApp.getUi()
    .createMenu('Citations')
    .addItem('Replace All', 'replaceCitationsWithSuperscripts')
    .addToUi();
}

function replaceCitationsWithSuperscripts() {
  Logger.log('Starting citation replacement');

  let counter = 1;                         // 1, 2, 3 …
  const nextNumber = () => String(counter++);

  /* basic patterns */
  const PAREN_PATTERN  = "\\((?:[^)]+)\\)";                // literal "( … )"
  const AUTHOR_YEAR_RE = /[\wÀ-ÖØ-öø-ÿ'’&.\-–0-9]+(?: et al\.)?,\s*[12]\d{3}/;
  const PUNCT_RE       = /[.,!?]/;                         // period, comma, …

  const pres = SlidesApp.getActivePresentation();

  pres.getSlides().forEach(slide => {
    slide.getPageElements().forEach(el => {
      if (el.getPageElementType() !== SlidesApp.PageElementType.SHAPE) return;

      const shape = el.asShape();
      const txt   = shape.getText();
      const raw   = txt.asString();
      if (!raw.trim()) return;

      const matches = txt.find(PAREN_PATTERN);
      if (!matches || matches.length === 0) return;

      /* Build replacement operations (left→right) first */
      const ops = [];

      matches.forEach(m => {
        const inner = m.asString().slice(1, -1);           // drop the ( )
        if (!AUTHOR_YEAR_RE.test(inner)) return;

        const supers = inner.split(';').map(() => nextNumber()).join(',');
        ops.push({
          start: m.getStartIndex(),
          end:   m.getEndIndex() - 1,                      // position of ")"
          supers
        });
      });

      if (ops.length === 0) return;

      /* Apply right→left so indices don’t shift */
      ops.sort((a, b) => b.start - a.start).forEach(op => {
        let { start, end, supers } = op;
        const full = shape.getText().asString();

        /* Trim *one* leading space (if any) so we don’t leave a gap */
        if (start > 0 && full.charAt(start - 1) === ' ') start--;

        /* Capture any spaces + single punctuation right AFTER the ')' */
        let trailSpace = '';
        let punct      = '';
        let i = end + 1;
        while (i < full.length && full.charAt(i) === ' ') { trailSpace += ' '; i++; }
        if (i < full.length && PUNCT_RE.test(full.charAt(i))) {
          punct = full.charAt(i);
          end = i;                                         // include punct in delete
        }

        /* Delete the old range (paren group, trailing space, punctuation) */
        const tr = shape.getText();
        tr.clear(start, end);

        const insertPos = start;

        /* Insert superscript digits/commas immediately after punctuation */
        const supRange = tr.insertText(insertPos + punct.length, supers);
        if (supRange) {
          supRange.getTextStyle()
                  .setBold(true)
                  .setItalic(false)                       // avoid inheriting italics
                  .setBaselineOffset(SlidesApp.TextBaselineOffset.SUPERSCRIPT);
        }
      });
    });
  });

  Logger.log('Citation replacement finished');
  SlidesApp.getUi().alert('Citations replaced successfully');
}