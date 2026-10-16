# OCR pipeline map

Paths below are relative to the repository root. This is a navigation map, not a guarantee that the implementation is defect-free; verify current code.

| Stage | Inspect | Contract |
| --- | --- | --- |
| Extraction | `aoq_flexible.py`: `extract_document`, PDF/image/workbook readers | Preserve `raw_text`, `tables`, and warnings; use native extraction before OCR where supported. |
| Mapping | `offline_ocr_mapper.py`: `PPMP_FIELDS`, `_label_value_candidates`, `_apply_candidate`, `_key_value_table_rows`, `_rows_from_table`, `map_document` | Explicit labels outrank guesses. A vertical key/value form produces one item; shared metadata fills blank item fields without adding a duplicate form row. |
| Local model | `offline_ocr_mapper.py`: `load_local_model`; `app.py`: upload handler | Honor `OCR_SEMANTIC_MODEL_PATH` and local files. Mapper helpers support fallback, while the live upload rejects an inactive semantic model. |
| Review controls | `templates/ppmp_type.html`, `static/js/ppmp-ocr-review.js`, review-save route in `app.py` | Keep the 12 labels, control indexes, saved payload, confidence edits, reviewer, and review status aligned. |
| Durable draft | `app.py`: OCR draft helpers and `/ppmp/ocr/` routes; `supabase/schema.sql` | `ppmp_ocr_drafts` is durable storage; temporary JSON alone is insufficient. Conversion uses saved reviewed values and updates the draft/link/audit in one transaction. |
| Official PPMP | `app.py`: `validated_ppmp_item_from_review`, `parse_currency_decimal` | Preserve canonical reviewed fields after alias normalization. Reject invalid amounts; do not silently make them zero. |
| APP handoff | `app.py`: `ppmp_source_payload`, APP generation and PPMP source API; `static/js/source-preview.js` | Use approved saved PPMP items, primary-key linkage, and recomputed stored-item totals without OCR remapping. Guard stale preview responses. |

## Extraction limits to distinguish from mapping bugs

- PDFs currently prefer native text at 20 or more characters; OCR handles fallback pages. PDF/image processing is capped at 30 pages/frames.
- Workbooks read cached formula results with `data_only=True`, propagate merged cells, and cap each sheet at 10,000 rows and 200 columns. This does not recalculate formulas.
- CSV extraction sniffs delimiters and caps rows at 10,000.

When a missing item lies beyond a limit, identify that cause before changing field matching. If changing a limit is requested, account for runtime cost and preserve warnings.
