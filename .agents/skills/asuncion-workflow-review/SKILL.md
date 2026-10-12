---
name: asuncion-workflow-review
description: Review procurement workflow correctness in the Asuncion Supply & Property Management System. Use for document transitions, approval permissions, totals, inventory updates, duplicate processing, or audit records. Do not use for OCR extraction accuracy or unrelated visual styling.
---

# Asuncion Procurement Workflow Review

## Review procedure
1. Read AGENTS.md and the relevant project documentation.
2. Identify the affected module, user role, starting state, action, and expected result.
3. Inspect the relevant routes in app.py, database operations in db.py, templates, and Supabase schema or migrations.
4. Trace the affected document relationships through the implemented workflow. Use the documented PPMP, APP, PR, AOQ, PO, NLP, IAR, Inventory, and RIS/ICS sequence as context; verify actual transitions in code.
5. Check that the server enforces role permissions, required fields, and valid approval transitions.
6. Check quantities, unit prices, subtotals, and totals against the source records.
7. Check that linked records use the correct identifiers and preserve document relationships.
8. Check that inventory changes happen at the intended stage and repeated submissions do not duplicate stock movements.
9. Check transaction handling so failures do not leave partially updated records.
10. Check that relevant actions produce accurate audit records.
11. Preserve human review before approval and the existing PostgreSQL architecture.

## Verification
- Review only unless the user requests a fix.
- Inspect relevant test scripts before running them.
- Use an isolated test database and synthetic records for checks that modify data.
- Do not reset databases or import legacy seed records without explicit authorization.
- Test the affected valid transition, an invalid or unauthorized transition, and repeated submission where relevant.
- If the database or dependencies are unavailable, report static findings separately from unverified runtime behavior.
- For requested fixes, keep changes focused and rerun the affected checks.

## Report
Provide:
- Workflow, roles, and code paths reviewed.
- Expected versus actual behavior.
- Findings with supporting evidence.
- Changes made, if requested.
- Checks run, results, and remaining limitations.

Do not claim the full workflow passes when only individual steps were checked.
