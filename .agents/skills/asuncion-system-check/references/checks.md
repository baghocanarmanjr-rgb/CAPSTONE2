# Existing check map

Verify the current code before use. Paths and commands are relative to the repository root; use the project's existing Python environment. Missing dependencies are a reported prerequisite, not permission to execute setup or reset scripts.

| Check | What it establishes | Effects / prerequisites |
| --- | --- | --- |
| `FINAL_WORKFLOW_REGRESSION_CHECK.py` | Expected source/AST patterns | Reads source text; no app or database execution. Does not prove route behavior. |
| `test_offline_ocr_mapper.py` | Free-form, full-field, table, metadata and quantity/specification mappings | Imports mapper/local model; no DB. Multiple main blocks run on direct execution. Can pass with mapper fallback. |
| `OCR_PPMP_APP_REGRESSION_TEST.py` | Basic mapped description/quantity/budget | Mapper only; no DB. Does not verify saved forms. |
| `OCR_PPMP_APP_FULL_FIELD_TEST.py` | Currency handling and reviewed-field serialization through PPMP/APP helpers | Imports `app` but calls pure helpers; current import does not initialize DB. Requires Flask/application import dependencies. Do not substitute test-client requests without isolation. |
| `OCR_FILETYPE_REGRESSION_TEST.py` | Native documents and scanned image/PDF extraction + mapping | Makes temporary synthetic fixtures; invokes installed Tesseract/local model; no DB. Native cases assert all 12 fields, scanned cases allow 9 or more exact matches. |
| `SYSTEM_SMOKE_TEST.py` | DB ping, SELECT table/user checks and sample workbook extraction | Reads configured PostgreSQL; no `init_db()` call in the inspected version. Not a full workflow or inference check. |
| `validate_installation.py` | Installation/init path | Explicitly imports `app` and calls `init_db()`; database mutation, not a read-only check. |
| App startup, Flask test-client requests, `/health`, login or GET `/ppmp` | HTTP behavior/readiness for the selected route | Can run initialization and dataset updates. Disposable PostgreSQL required. A GET is not a read-only guarantee here. |

## Evidence to keep separate

- Passing mapping assertions may use lexical fallback; inspect `offline_ocr_mapper.model_status()` for local semantic model readiness.
- OCR model status loads/encodes locally; FastText model status checks presence/metadata. For FastText inference, exercise the actual classifier path with a known input and inspect its result.
- `/health` combines prerequisite signals and DB connectivity; it does not validate full extraction accuracy, predictions, approval transitions or stock movements.
- `TEST_OFFLINE_MODE.ps1` does not inspect Python exit codes; `TEST_OFFLINE_AI.ps1` misses the final classification exit code. Inspect direct command outcomes instead of trusting their success text.
- `inventory_dataset.get_status()` calls `ensure_schema()`, which writes metadata and drops a legacy table. Workbook synchronization is also a database mutation.

For workflow tests, set an isolated PostgreSQL URL before importing the app, use synthetic records, and assert the resulting data. Do not clear or reseed a user's database to make checks pass.
