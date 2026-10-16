---
name: asuncion-system-check
description: Verify Asuncion system readiness or regressions after runtime changes, and diagnose failed OCR, model, database, or workflow checks. Use for testing requests rather than documentation-only edits.
---

# Asuncion System Checks

Identify the requested evidence: source consistency, parsing accuracy, prerequisite readiness, database connectivity, or a complete workflow. Read [the check map](references/checks.md) and inspect the current scripts before choosing the smallest relevant set.

## Choose checks by their actual effects

- For skills/documentation-only changes, validate their structure and referenced paths; no application runtime test is required solely for those edits.
- Start with relevant static or parser checks when they answer the question. Do not call a source-string assertion a runtime regression test.
- Treat any Flask request or app startup as potentially mutating. First-request initialization applies schema, repairs stored records, updates accounts, and synchronizes datasets. `validate_installation.py` explicitly initializes the database. Use an explicitly disposable PostgreSQL target before importing `app` for these checks; never rely on a temporary SQLite filename.
- `SYSTEM_SMOKE_TEST.py` checks database reads and sample extraction, not the full procurement chain. Choose workflow checks against synthetic records only when that level of evidence is needed.
- Preserve offline execution after dependencies/models are installed. Verify local OCR model activity separately from mapping assertions, which may succeed using fallback signals.

## Read results precisely

Inspect each command's actual exit code and useful output. `TEST_OFFLINE_MODE.ps1` can print success after a failed Python check; `TEST_OFFLINE_AI.ps1` does not check its final classification command's exit code. A banner alone is insufficient.

FastText `model_status()` verifies files and metadata compatibility, not classifier loading or inference. `/health` is authenticated and may initialize data; a ready response is prerequisite evidence, not proof of correct model predictions or full OCR/workflow behavior. For an inference claim, run an appropriate known-input prediction and compare its output.

For a changed workflow, inspect the relevant current checklist and assert saved state, document links, totals, stock deltas, and audit records. Use `FINAL_LIVE_TEST_CHECKLIST.txt` for PPMP review/approval and edit resets; verify the broader chain from source when requested.

Report the scope tested, commands/checks and outcomes, prerequisites missing, and untested stages. A limited passing check should remain a limited claim. Do not run installers, fetch models, reset data, or perform unrelated repairs merely to produce a green result.
