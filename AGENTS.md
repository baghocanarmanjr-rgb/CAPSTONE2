# Project Instructions

## Project overview
Municipality of Asuncion Supply & Property Management System.
Read README.txt and INSTALLATION_SUPABASE_OCR_GUIDE.md for setup details.
Verify documentation against the relevant source code before making changes.

## Technology
- Python Flask / Waitress application.
- Supabase PostgreSQL accessed through db.py using psycopg.
- Local Tesseract OCR and native document extraction.
- Local FastText models for NLP.
- HTML templates, CSS, and JavaScript.

## Important files
- app.py: application routes and procurement workflows.
- db.py: PostgreSQL connection layer.
- aoq_flexible.py: document extraction and AOQ parsing.
- offline_ocr_mapper.py: offline OCR mapping.
- templates/: application pages.
- static/: styles, scripts, and images.
- supabase/schema.sql and supabase/migrations/: database schema.

## Development rules
- Work on the activity branch feature/ai-skills.
- Keep changes focused on the requested task.
- Preserve offline operation after dependencies and models are installed.
- Use PostgreSQL through the existing database layer; do not reintroduce SQLite.
- Preserve human review before procurement document approval.
- Preserve the dark-green sidebar, split login layout, and responsive design.
- Never commit real credentials or private uploaded documents.
- Do not reset databases or run MIGRATE_LEGACY_DATA.ps1 -ConfirmReset without explicit authorization.

## Validation
- Inspect relevant tests before running them to understand their effects.
- For runtime changes, run relevant checks using test data.
- With local Supabase running, python .\SYSTEM_SMOKE_TEST.py is the documented smoke test.
- For OCR changes, compare extracted fields with the original sample documents.
- For workflow changes, check affected approvals, totals, inventory updates, and audit records.
- Report what changed, what was tested, and any checks that could not run.
