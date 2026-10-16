# Procurement transition map

Verify these anchors in the current `app.py` and Supabase schema before editing. Desired duplicate/rollback checks are not claims that every existing route already provides them.

| Operation | Existing contract / evidence |
| --- | --- |
| Review PPMP | Saved nonempty items and `review_confirm=yes` are required for Draft -> Reviewed. |
| Approve PPMP | The saved status must be Reviewed before Approved. |
| Edit PPMP | A downstream APP blocks editing. An allowed edit resets status to Draft and clears review/approval metadata. |
| Generate APP | Use an approved PPMP's saved items without remapping OCR; source locking and duplicate checks are present. One APP row is inserted per PPMP item, so `app_plan.ppmp_id` is intentionally one-to-many. |
| Later source selection | Read `next_available_records` for PR, AOQ, PO, NLP and IAR; inspect `ris_ics` for issuance eligibility. Do not assume all links have database uniqueness constraints. |
| NLP -> IAR | Approved NLP with Acceptable or Needs Review can proceed; Needs Recanvass and Reject do not. |
| IAR receipt | Creation does not add stock. Approval adds inventory. Current approval uses separately committed inventory writes and then status, so inspect partial-write and replay risks when working here. |
| RIS/ICS issue | Preparation does not deduct stock. Approval checks positive quantities against available stock, then deducts stock and records the ledger/status in a transaction. Current `BEGIN IMMEDIATE` translation does not supply a row lock or guarantee safe simultaneous approvals. |

## Ownership and permissions

`ensure()` requires login for normal routes; `/users` has an explicit Admin guard. Determine the real guard on each affected approval route. A review checkbox does not establish which user roles may approve.

For atomic stock/state/audit changes, inspect `db.Connection`, `exec_db`, and `log`. A nested helper that opens a fresh committed connection is outside an outer transaction. When concurrency is in scope, lock and recheck the affected source/status/stock rows in the same transaction; verify outcomes with repeated and simultaneous submissions.

Use `FINAL_LIVE_TEST_CHECKLIST.txt` for the PPMP review/edit sequence. The older general checklist omits its Reviewed/Approved gates, so current code and targeted evidence take precedence.
