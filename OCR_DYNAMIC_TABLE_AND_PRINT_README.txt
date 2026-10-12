ASUNCION PSMS - DYNAMIC OCR TABLE + PRINT BUILD
================================================

WHAT IS IMPLEMENTED
1. PPMP OCR accepts PDF, PNG/JPG, BMP/TIFF, DOCX, XLSX/XLSM, CSV, and TXT.
2. OCR raw text is parsed into an editable/selectable structured table.
3. Users can select rows, edit cells, add/remove rows, add columns, rename headers, and manually map columns to PPMP fields.
4. Only selected and user-verified rows are submitted.
5. Server validates allowed PPMP fields before inserting into PostgreSQL/Supabase.
6. Large OCR text is staged on the local server filesystem instead of being stored directly in Flask's browser cookie session.
7. Audit trail records PPMP records created from OCR.

PRINTING CONFIRMED
The system includes dedicated printable document views for:
- PPMP
- APP
- Purchase Request (PR)
- Purchase Order (PO)
- Inspection and Acceptance Report (IAR/AIR)
- RIS / ICS

Each print page includes a "Print document" button and uses browser printing with A4 print CSS.
AOQ and NLP are review/verification modules; official downstream procurement/property documents above remain printable.

TEST FILES
See sample_files/ocr_deployment_test for PPMP and AOQ OCR test files plus the complete end-to-end test guide.

START
1. Start Docker Desktop.
2. From capstone folder run:
   powershell -ExecutionPolicy Bypass -File .\START_SYSTEM.ps1
3. Open http://127.0.0.1:5000
