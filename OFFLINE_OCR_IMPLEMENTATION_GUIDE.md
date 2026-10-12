# Offline PPMP OCR + Semantic Mapping

## One-time installation (internet available)
1. Start Docker Desktop and local Supabase.
2. From the `capstone` folder run:
   `powershell -ExecutionPolicy Bypass -File .\INSTALL_OFFLINE_OCR_AI.ps1`
3. Install Tesseract OCR for Windows and set `TESSERACT_CMD` only if it is not in the standard location.

The semantic model is stored locally under `models/ocr_mapper/all-MiniLM-L6-v2/`. Runtime code loads it from disk only.

## Normal offline startup
1. Start Docker Desktop.
2. Start local Supabase (`npx supabase start` if needed).
3. Disconnect internet if you want to verify true offline operation.
4. Run `powershell -ExecutionPolicy Bypass -File .\TEST_OFFLINE_MODE.ps1`.
5. Run `powershell -ExecutionPolicy Bypass -File .\START_SYSTEM.ps1`.

## PPMP OCR workflow
Upload supported document -> local extraction/OCR -> semantic/fuzzy/pattern/context mapping -> temporary `OCR-TEMP-*` rows in the normal PPMP table -> Review/Edit -> select verified rows -> `Create PPMP from Verified OCR`.

The source document does not need exact PPMP header names. Low-confidence fields are never treated as certain; they require human review.

## Header/account changes
The old `Offline system` badge is replaced by a local live clock. This is a visual change only; offline capability remains. The standalone Sign Out button is removed. Click the avatar/user area for My Account, Change Password, and Sign Out.
