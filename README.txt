MUNICIPALITY OF ASUNCION SUPPLY & PROPERTY MANAGEMENT SYSTEM
REVISED SUPABASE + OFFLINE OCR BUILD

START HERE:
1. Read INSTALLATION_SUPABASE_OCR_GUIDE.md
2. Run SETUP_LOCAL_SUPABASE.ps1 once while internet is available.
3. Optionally run MIGRATE_LEGACY_DATA.ps1 -ConfirmReset to import packaged legacy records.
4. Run START_SYSTEM.ps1.
5. Open http://127.0.0.1:5000

Database runtime: Supabase PostgreSQL (no SQLite runtime).
OCR: local Tesseract + native extraction for PDF/DOCX/XLSX/CSV/TXT where possible.
UI: approved persistent dark-green sidebar and split login redesign.
