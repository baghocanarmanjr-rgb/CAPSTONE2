# Asuncion Supply & Property Management System
## Supabase + Offline OCR Revised Build

This build replaces the SQLite runtime with **Supabase PostgreSQL**, applies the approved persistent-sidebar UI to the whole authenticated application, and strengthens local document extraction/OCR.

## 1. What changed

### UI
- The approved dark-green left navigation is now the shared desktop shell for Dashboard, PPMP, APP, PR, AOQ, PO, NLP Verification, IAR/AIR, Inventory, RIS/ICS, Reports, Audit Trail, and User Management.
- The login screen uses the approved split-panel redesign.
- The dashboard now uses the approved welcome banner, KPI cards, procurement pipeline, pending-review table, NLP card, and recent activity layout.
- Mobile remains responsive: the sidebar becomes a drawer below 901 px.

### Database
- `sqlite3` is no longer used by the application runtime.
- All operational queries now go through `db.py` and PostgreSQL (`psycopg`).
- The target database is Supabase PostgreSQL. The default connection is the local Supabase CLI database at `127.0.0.1:54322`.
- PostgreSQL schema: `supabase/schema.sql`.
- Supabase migration: `supabase/migrations/202610040001_psms_schema.sql`.
- Existing records from the packaged legacy database were exported into `supabase/legacy_seed.sql`. The old `.db` files are not part of this revised runtime.

### OCR/document extraction
- Digital PDF text is extracted natively before OCR is attempted.
- Scanned PDFs/images use a confidence-scored Tesseract ensemble with multiple page-segmentation modes.
- Three conservative image variants are evaluated so punctuation and decimal points are less likely to be destroyed by aggressive thresholding.
- OCR output is rebuilt by detected lines/word positions to preserve line structure more accurately.
- Multi-page TIFF/images are supported (first 30 frames/pages).
- DOCX, XLSX/XLSM, CSV and TXT use native structured extraction instead of OCR whenever possible.
- AOQ flexible table parsing remains in place and human review is still required before approval.

> Important: no OCR engine can guarantee perfect word-for-word recognition for every possible scan. Blur, low resolution, handwriting, skew, compression, unusual fonts, or damaged pages can still cause errors. For procurement records, keep the review/approval step and compare extracted values against the source document.

## 2. Windows prerequisites

Install these **while internet is available**:

1. **Python 3.11 or later** and enable `Add Python to PATH`.
2. **Node.js 20 or later**.
3. **Docker Desktop** and start Docker Desktop before Supabase.
4. **Tesseract OCR 5.x for Windows**. The default expected path is:
   `C:\Program Files\Tesseract-OCR\tesseract.exe`

The Supabase CLI local stack uses Docker on Windows. The first `supabase start` downloads container images, so perform the initial setup while online. After the images and Python/npm dependencies are installed, the local application and local database can run without internet.

## 3. One-command local Supabase setup

Open **PowerShell** in the `capstone` folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\SETUP_LOCAL_SUPABASE.ps1
```

The script:
- installs Python requirements;
- installs the Supabase CLI locally through npm when needed;
- runs `npx supabase init` if `supabase/config.toml` does not yet exist;
- runs `npx supabase start`;
- connects to local PostgreSQL at port `54322`;
- applies the PSMS PostgreSQL schema.

Supabase Studio is normally available at:

```text
http://127.0.0.1:54323
```

## 4. Optional migration of the packaged legacy records

A PostgreSQL-compatible seed was generated from the old SQLite database before SQLite was removed from the revised package.

Run this **once**, after local Supabase has been initialized:

```powershell
powershell -ExecutionPolicy Bypass -File .\MIGRATE_LEGACY_DATA.ps1 -ConfirmReset
```

This intentionally resets the **local Supabase database**, reapplies the schema, then imports the records in `supabase/legacy_seed.sql`. Do not run it after entering new production data unless you intentionally want to rebuild the local database.

For a clean database, skip this step.

## 5. Start the application

```powershell
powershell -ExecutionPolicy Bypass -File .\START_SYSTEM.ps1
```

Open:

```text
http://127.0.0.1:5000
```

For a brand-new empty database, the application seeds an administrator account. Set a strong initial password before first start:

```powershell
$env:PSMS_INITIAL_ADMIN_PASSWORD = "Use-A-Strong-Password-Here"
$env:PSMS_SECRET_KEY = "replace-with-a-long-random-secret"
.\START_SYSTEM.ps1
```

If you do not set `PSMS_INITIAL_ADMIN_PASSWORD`, the development fallback remains `admin123`. Change it immediately in User Management.

## 6. Tesseract configuration

Test Tesseract:

```powershell
tesseract --version
```

If Windows cannot find it, set:

```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Then start the system from the same PowerShell window.

For best OCR results:
- scan at about 300 DPI or higher;
- keep pages upright and flat;
- avoid shadows and JPEG artifacts;
- prefer PDF with embedded text when available;
- use original Office files instead of screenshots when possible.

## 7. Database environment variables

Default local connection:

```powershell
$env:SUPABASE_DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
```

To use a hosted Supabase project or a hardened self-hosted Supabase server, replace `SUPABASE_DB_URL` with that PostgreSQL connection string **before** starting Flask.

Do not commit production passwords or service credentials to Git.

## 8. Offline-first architecture

For this municipality workflow the recommended offline architecture is:

```text
Browser on local PC/LAN
        |
        v
Flask / Waitress application
        |
        v
Local Supabase PostgreSQL (Docker)
        |
        +--> local Tesseract OCR
        +--> local FastText model
        +--> local Excel/Office source files
```

The application does not require a cloud round-trip for normal operations. This is more reliable for an offline office than attempting to queue every relational transaction in browser storage.

If the municipality later wants cloud replication, treat that as a separate controlled synchronization service. Do not use two independently writable PostgreSQL/Supabase databases without a conflict-resolution design, because procurement approvals and inventory deductions must remain transactionally consistent.

## 9. Production deployment note

The Supabase CLI local stack is excellent for capstone/demo/development and offline single-machine use, but it is not hardened as an internet-facing production service. For a real municipal LAN/production deployment, use the official **self-hosted Supabase Docker** deployment, configure strong secrets, backups, firewall rules, TLS/reverse proxy where required, and expose only the services needed by the office.

Never expose the default local CLI ports directly to the public internet.

## 10. Validation

After the database is running:

```powershell
python .\SYSTEM_SMOKE_TEST.py
```

The test is non-destructive. It verifies:
- PostgreSQL connectivity;
- required PSMS tables;
- at least one system user;
- structured AOQ sample-file extraction.

Also verify manually:
1. Sign in.
2. Open every module and confirm the persistent sidebar/layout.
3. Upload one clean image, one scanned PDF, and one native DOCX/XLSX AOQ sample.
4. Compare extracted values with the source.
5. Run PPMP → APP → PR → AOQ → PO → NLP → IAR → Inventory → RIS/ICS with test records.
6. Verify Reports and Audit Trail.
7. Restart Docker/Supabase and confirm saved data remains available.

## 11. Key revised files

- `app.py` — Flask routes and PostgreSQL-backed workflow.
- `db.py` — Supabase/PostgreSQL connection layer.
- `aoq_flexible.py` — structured extraction + improved local OCR.
- `inventory_dataset.py` — PostgreSQL-backed inventory source repository.
- `templates/base.html` — approved shared sidebar shell.
- `templates/login.html` — approved split login redesign.
- `templates/dashboard.html` — approved dashboard redesign.
- `static/css/reference-layout.css` — revised responsive presentation.
- `supabase/schema.sql` — full PostgreSQL schema.
- `supabase/legacy_seed.sql` — optional one-time legacy data import.
- `SETUP_LOCAL_SUPABASE.ps1` — Windows local DB setup.
- `MIGRATE_LEGACY_DATA.ps1` — optional migration reset/import.
- `START_SYSTEM.ps1` — database check + app launch.
