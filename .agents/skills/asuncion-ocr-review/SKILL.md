---
name: asuncion-ocr-review
description: Review or troubleshoot document extraction and OCR field mapping in the Asuncion Supply & Property Management System. Use for incorrect extracted text, missing table rows, mismatched procurement fields, or OCR regression checks. Do not use for unrelated UI or database tasks.
---

# Asuncion OCR Review

## Review procedure
1. Read AGENTS.md and the relevant project documentation.
2. Identify the affected document type, reported issue, and expected result.
3. Inspect the relevant code in aoq_flexible.py, offline_ocr_mapper.py, and the calling routes in app.py.
4. Trace extracted values into the affected form or table.
5. Prefer native extraction for supported digital documents; preserve local OCR for scanned documents.
6. Compare output against the original sample document. Check identifiers, descriptions, quantities, units, prices, decimal points, totals, and row alignment where applicable.
7. Flag missing or uncertain values instead of inventing replacements.
8. Preserve human review before approval and offline operation after setup.

## Verification
- Use sample_files/ or user-provided test documents.
- Inspect relevant OCR test scripts before running them.
- Run only checks relevant to the affected extraction or mapping behavior.
- If the source document, dependencies, or model is unavailable, explain what could not be verified.
- Review only unless the user requests a fix. For requested fixes, keep changes focused and rerun the affected checks.

## Report
Provide:
- Document and code paths reviewed.
- Expected versus actual extracted values.
- Findings with supporting evidence.
- Changes made, if requested.
- Checks run, results, and remaining limitations.

Do not claim extraction is correct without comparing it with the source.

