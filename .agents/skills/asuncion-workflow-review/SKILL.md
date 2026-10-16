---
name: asuncion-workflow-review
description: Fix or review Asuncion procurement transitions, approval gates, document links, stock movements, repeated submissions, and audit consistency. Use for workflow behavior rather than extraction accuracy or visual styling.
---

# Asuncion Procurement Workflow Review

Use the requested review or fix scope. Identify the source record, user role, starting status, submitted action, and expected resulting documents or stock movement. Read [the transition map](references/transitions.md) for the affected path.

## Trace the whole affected operation

- Follow the actual route in `app.py`, template/form payload, database writes, and audit entry. Use `next_available_records` and the schema to establish document eligibility and relationships; do not infer rules from a screen label alone.
- Check state and permission guards on the server. `review_confirm=yes` is a form confirmation, not a role policy or durable proof of review. The existing approval routes are not universally Admin-only; preserve intended permissions and identify gaps without inventing a new role policy.
- Preserve PPMP Draft -> Reviewed -> Approved, edit resets, and the approved-source gate for APP. APP can contain multiple rows linked to the same PPMP, one per item.
- Recompute relevant amounts from saved items and preserve source identifiers. Check both upstream eligibility and downstream side effects when changing a transition.
- Stock receipt belongs to IAR approval; stock deduction belongs to RIS/ICS approval. Replaying a request or failing midway must not silently duplicate stock or leave a partial operation.
- Inspect the transaction actually used. `exec_db()` and `log()` commit separately; `BEGIN IMMEDIATE` becomes plain PostgreSQL `BEGIN`. Existing code is not blanket evidence of atomicity or concurrency safety. For a requested fix involving multiple writes, use one connection with explicit commit/rollback and the appropriate locked status check.

## Verify observable outcomes

Use synthetic records in an explicitly disposable PostgreSQL database. Even a first GET can initialize or repair data. Inspect selected scripts and [the test map](../asuncion-system-check/references/checks.md) before running them.

For the affected transition, verify a valid action, an invalid state, relevant permission rejection, and a repeated submission. When changing stock or duplicate protection, also check rollback after a failure and concurrent submissions where practical. Assert exact record links, quantities, status, and audit outcomes rather than a successful HTTP response alone.

Keep fixes within the requested workflow. Report concrete findings with code evidence and distinguish tested behavior from static conclusions or untested concurrency. Do not present an individual step as proof of the full procurement chain.
