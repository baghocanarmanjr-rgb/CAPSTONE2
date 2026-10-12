# Dynamic OCR verification implementation

This build integrates the flexible OCR parser directly into the PPMP workflow.

Workflow: Upload document -> raw extraction -> structured editable table -> user selects/edits/re-maps -> server validates -> PPMP record -> Print.

Supported PPMP OCR uploads: PDF, PNG/JPG, BMP/TIFF, DOCX, XLSX/XLSM, CSV and TXT.

Important: automatic OCR mapping is assistive. Users must review the structured table before creating PPMP records.

## Printing
The system includes dedicated browser-print views for PPMP, APP, Purchase Request, Purchase Order, IAR/AIR and RIS/ICS. Each print page has a Print document button using the browser's native print dialog and A4 print CSS.

## OCR staging
Large OCR text is staged in `temp/ppmp_ocr` and only a random token is kept in the Flask session. This avoids exceeding browser cookie limits for large documents.
