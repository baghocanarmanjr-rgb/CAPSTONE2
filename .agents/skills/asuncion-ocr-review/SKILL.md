---
name: asuncion-ocr-review
description: Fix or review Asuncion document extraction, OCR mapping, and reviewed PPMP fields through saving and APP generation. Use for missing rows, incorrect amounts, lost fields, or OCR regressions.
---

# Asuncion OCR Review

Use the requested review or fix scope. Start with the source document, its type, and the exact expected fields. Read [the pipeline map](references/pipeline.md) for the affected stage; confirm current functions before editing.

## Preserve these contracts

- Keep the 12 canonical `PPMP_FIELDS`, their order, and `ocr_field_0` through `ocr_field_11` aligned across Python, templates, and JavaScript. Missing review controls must not silently erase saved values.
- Prefer native extraction for digital documents and local Tesseract for scans. Preserve offline model loading. A mapper fallback passing a unit check does not establish that the live upload's required semantic model is active.
- Explicit source labels outrank semantic or lexical guesses. Preserve colons, decimal punctuation, long descriptions, and quantity/specification combinations. Distinguish a vertical form from a table of separate items.
- Leave missing or uncertain values reviewable. Preserve the distinction between invalid currency and a valid zero; use `parse_currency_decimal` and the existing validation path for critical saves.
- Trace reviewed fields into durable draft storage, conversion, the saved PPMP, and APP source serialization. Reviewed values must survive without a second OCR mapping pass. Preserve row locking, conversion linkage, and human approval gates already implemented.
- For source-preview bugs, inspect `static/js/source-preview.js` so an older response cannot overwrite a newer selection.

## Verify the changed stage

Compare every affected value with the original document, including row count, identifiers, quantity/specifications, budget, currency punctuation, and all 12 fields when applicable. A saved-field fix also needs a reviewed-value round trip, not extraction alone.

Choose relevant existing checks using [the test map](../asuncion-system-check/references/checks.md). Inspect their current side effects first. HTTP requests initialize the database; use an explicitly isolated PostgreSQL database for those checks. Run focused checks after a requested fix; do not change unrelated workflow behavior.

Report expected versus observed values, changed paths, and what was actually checked. Separate lexical fallback results, semantic-model readiness, and end-to-end OCR evidence. If the source or a required dependency is missing, identify the unverified stage.

