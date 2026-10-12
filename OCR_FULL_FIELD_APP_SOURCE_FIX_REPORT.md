# OCR Full-Field / PPMP / APP Source Fix Report

## Scope

This revision fixes the data-integrity path requested for the Municipality of Asuncion PSMS:

`source file -> native extraction/OCR -> mapped draft -> human review -> PostgreSQL OCR draft -> official PPMP -> APP Source PPMP -> generated APP`

It also adjusts the login screen proportions while preserving the existing green/white design.

## Root causes found

### 1. Valid PHP amounts were silently converted to zero

`app.py::to_float()` only removed the peso symbol and commas. A reviewed value such as `PHP 80,000.00` therefore raised a float-conversion error and the old catch block returned `0.0`. This affected PPMP totals, APP preview totals, generated APP totals, and downstream totals even when the item JSON still contained the correct text.

Fix: a centralized `parse_currency_decimal()` now accepts common Philippine currency forms and returns `None` for invalid/blank input instead of silently converting it to zero. Critical OCR/PPMP save paths reject invalid amounts.

### 2. OCR review and official PPMP creation were not enforcing one canonical reviewed payload

The reviewed draft was persisted, but the official conversion path still used permissive conversions such as `to_float(... or 0)` and generic fallback/default behavior. This allowed a correct reviewed value to become a different stored/derived value.

Fix: `normalize_reviewed_ocr_fields()` whitelists all 12 PPMP fields and `validated_ppmp_item_from_review()` creates the official PPMP only from the persisted reviewed database row. OCR, semantic mapping, the original file, Excel rows, and session values are not consulted during conversion.

### 3. Source-of-funds normalization could silently insert a default

`normalize_excel_row()` used `GF` as a fallback for Source of Funds. That was acceptable for some legacy Excel flows but violated the requirement that reviewed OCR values remain the source of truth.

Fix: the normalizer no longer inserts `GF` when the reviewed field is empty. Canonical reviewed fields are re-applied after alias generation so aliases cannot replace official values.

### 4. APP Source PPMP preview was page-rendered static data, not a live selected-record lookup

The APP dropdown embedded summary data in HTML `data-*` attributes when the page loaded. The preview did not request the exact selected PPMP from PostgreSQL. It also showed only a subset of fields and relied on the parent `ppmp.total`, which could be zero because of the currency bug.

Fix: APP now calls `/api/ppmp/<id>/source` using the selected PPMP primary key. The API loads that exact official PPMP and returns all 12 fields from its saved item JSON. The browser replaces the whole preview on each selection and protects against stale/racing responses.

### 5. APP generation used permissive amount conversion and separate autocommitted inserts

The old APP generation path converted each amount with the permissive helper and inserted APP records one at a time. A bad conversion could produce zero, and a later failure could leave partial records.

Fix: the selected PPMP is loaded by primary key, its item budgets are strictly validated, exact item dictionaries are copied to APP, and APP inserts plus source-status/audit updates run in one transaction. Duplicate submissions are blocked.

### 6. Structured document tables were not classified robustly

The PPMP mapper treated tables too uniformly. Two-column/key-value forms from DOCX/XLSX/CSV could be interpreted as multiple procurement items. Multi-item tables could also lose technical specifications when Qty and Technical Requirement both mapped to Quantity/Size. Shared values such as Funding and Procurement Method outside a table were not inherited into each row.

Fix: the mapper now distinguishes vertical key/value forms from row-based multi-item tables, searches for a semantic header row, combines quantity + specification columns, and inherits explicit shared metadata without overwriting row-specific values.

### 7. CSV delimiter detection could fail on legitimate procurement text

`csv.Sniffer()` could infer an invalid delimiter from content containing many repeated letters/characters, raising `ValueError: bad delimiter value`.

Fix: delimiter sniffing is restricted to common delimiters `, ; tab |` with a safe fallback to the standard CSV dialect.

### 8. Existing OCR-created PPMP records could remain corrupted after upgrading

Older builds may already have a converted OCR draft linked to a PPMP whose parent total or item fields differ from the reviewed draft.

Fix: startup now performs an idempotent repair for converted OCR PPMPs that still have a persisted reviewed draft. It reconstructs all 12 official fields from that reviewed draft, preserves stable item/source metadata, repairs the total, and writes an audit entry. Invalid drafts are skipped rather than silently defaulted.

## Main files changed

- `app.py`
- `offline_ocr_mapper.py`
- `aoq_flexible.py`
- `templates/app.html`
- `templates/ppmp_home.html`
- `static/js/source-preview.js`
- `static/css/reference-layout.css`
- `test_offline_ocr_mapper.py`

New tests/documentation:

- `OCR_FILETYPE_REGRESSION_TEST.py`
- `OCR_PPMP_APP_FULL_FIELD_TEST.py`
- `OCR_FULL_FIELD_APP_SOURCE_END_TO_END_CHECKLIST.txt`
- `OCR_FULL_FIELD_APP_SOURCE_FIX_REPORT.md`

## Database changes

No new table is required for this revision. The existing `ppmp_ocr_drafts`, `ppmp`, and `app_plan` structures are sufficient. The reviewed draft remains the durable source of truth until conversion.

## Confirmed extraction regression results in the build environment

The updated extractor/mapper passed exact 12-field tests for:

- TXT
- CSV
- XLSX
- XLSM
- DOCX
- native-text PDF
- PNG OCR
- JPG OCR
- BMP OCR
- TIFF OCR
- scanned PDF OCR

The multi-item regression also passed, including shared Funding and Procurement Method context and merged Qty + Technical Requirement into the PPMP Quantity/Size field.

## Static validation completed

- Python compilation: PASS
- Jinja templates: 27/27 PASS
- JavaScript syntax: PASS
- Existing OCR mapper regression tests: PASS
- Flexible OCR mapper regression test: PASS
- Currency and full-field PPMP/APP helper logic: PASS using the exact functions extracted from `app.py`

A live PostgreSQL/Supabase browser integration test cannot be run inside this build container because the user's Windows Docker/Supabase instance is not available here. The included end-to-end checklist is intended for the real deployment machine.
