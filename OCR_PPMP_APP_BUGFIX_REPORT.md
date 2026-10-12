# OCR → PPMP → APP Bug Fix Report

## Root cause 1: reviewed OCR data was not durable
The existing build stored OCR state in `temp/ppmp_ocr/*.json` referenced by the Flask session. `Save Review` only rewrote that temporary JSON file. It never inserted a reviewed OCR record into PostgreSQL.

### Fix
Added `ppmp_ocr_drafts` in PostgreSQL. Extracted OCR rows are staged there and `Save Review` updates the durable row, reviewer, timestamp, confidence metadata, and lifecycle status.

## Root cause 2: OCR PPMP items skipped downstream normalization
Excel-origin PPMP rows pass through `normalize_excel_row()`, which adds aliases used throughout APP/PR/AOQ/PO. OCR-origin rows previously stored only the 12 official fields, creating an inconsistent item shape.

### Fix
Verified OCR data now passes through the same normalization before the official PPMP is inserted. APP also shows a detailed source preview from the official PPMP JSON.

## Root cause 3: semantic model setup was optional and startup did not enforce it
The Supabase setup only printed a later install command, while startup printed model status and continued. OCR therefore fell back and showed the warning.

### Fix
Supabase setup now installs the local semantic model automatically when absent. Startup blocks when the semantic mapper, Tesseract, or FastText model is unavailable. `/health` reports all required offline components.

## Integrity and duplicate protection
OCR→PPMP conversion locks the draft, inserts the PPMP, marks the draft converted, stores the official PPMP id, and writes the audit record in one transaction. A unique partial index on `official_ppmp_id` prevents duplicate conversion.
