# Revision Report

## Bugs / architecture problems found

1. **SQLite was hard-wired into the runtime.** `app.py` opened `instance/psms.db` directly and `inventory_dataset.py` independently opened the same SQLite database. This made a Supabase migration impossible without changing two data-access paths.
2. **SQLite-only SQL was spread through the code.** Examples included `PRAGMA table_info`, `AUTOINCREMENT`, `COLLATE NOCASE`, `BEGIN IMMEDIATE`, `?` placeholders, and SQLite-tolerated double-quoted string literals such as `status="Approved"`.
3. **The identifier generator used SQLite locking semantics.** `BEGIN IMMEDIATE` is not PostgreSQL/Supabase syntax and would not provide the intended behavior after migration.
4. **The inventory workbook repository still created and synchronized SQLite tables.** This was a second hidden database dependency even if the main Flask connection were changed.
5. **The old smoke test explicitly created a temporary SQLite database**, so it would incorrectly validate the obsolete architecture.
6. **PPMP OCR bypassed the stronger document extraction path.** It called `pytesseract.image_to_string(Image.open(...))` directly and therefore ignored PDF native text, Office files, structured tables, OCR preprocessing, and useful warnings.
7. **The OCR ensemble selected output mainly by text length.** Longer OCR output can be noisier; it did not use word confidence to choose the best candidate.
8. **Image OCR did not preserve line structure as deliberately as needed.** It returned Tesseract's plain string rather than rebuilding lines from recognized word positions.
9. **Multi-frame TIFF/image files were not fully processed.** Only the initially opened frame was used.
10. **The desktop navigation was still implemented as an off-canvas drawer.** The desired reference design requires a persistent left sidebar.
11. **The navigation JavaScript depended on the edge-reveal element.** Removing that element for the persistent layout without changing JavaScript would cause `addEventListener` calls on `null`.
12. **Login and dashboard still used the earlier visual structure.** They did not match the supplied split login and dashboard reference boards.
13. **The application had no offline Supabase strategy.** It assumed a local SQLite file and had no documented local PostgreSQL/Supabase deployment path.

## Main fixes applied

- Added `db.py` using `psycopg` and a Supabase/PostgreSQL connection string.
- Added a complete PostgreSQL schema and timestamped Supabase migration.
- Reworked the document number sequence with PostgreSQL `INSERT ... ON CONFLICT ... RETURNING` so concurrent number allocation is safe.
- Converted the inventory dataset repository to the same PostgreSQL connection layer.
- Removed packaged `.db` runtime files and exported their existing data to `supabase/legacy_seed.sql`.
- Added Windows setup, start, and one-time legacy migration PowerShell scripts.
- Strengthened OCR preprocessing, confidence-based candidate selection, layout-aware line reconstruction, and multi-frame image handling.
- Routed PPMP OCR through the same flexible extraction engine used for AOQ documents.
- Applied the persistent approved sidebar shell globally to authenticated pages.
- Rebuilt login and dashboard templates to match the supplied target design.
- Fixed desktop/mobile navigation JavaScript so the persistent sidebar remains interactive and mobile still uses a drawer.
- Replaced the SQLite smoke test with a non-destructive Supabase readiness test.

## Migration sequence

1. Install Python 3.11+, Node.js 20+, Docker Desktop, and Tesseract 5.
2. Run `SETUP_LOCAL_SUPABASE.ps1` while internet is available at least once so Docker images and npm/Python packages are cached locally.
3. For a clean database, start the app immediately.
4. To bring over the records contained in the former packaged SQLite database, run `MIGRATE_LEGACY_DATA.ps1 -ConfirmReset` once.
5. Set strong `PSMS_SECRET_KEY` and `PSMS_INITIAL_ADMIN_PASSWORD` environment variables.
6. Run `START_SYSTEM.ps1`.
7. Run `SYSTEM_SMOKE_TEST.py` and then perform the manual procurement workflow test described in the installation guide.

## OCR accuracy note

The revised implementation is designed for substantially better local accuracy, but **no OCR system can truthfully guarantee exact word-for-word results for every uploaded scan**. Source quality determines the ceiling. For procurement documents, extracted values must remain reviewable before approval; the revised workflow preserves that control.
