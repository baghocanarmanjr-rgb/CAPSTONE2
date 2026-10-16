---
name: asuncion-database-change
description: Change Asuncion PostgreSQL queries, transactions, schema, or Supabase migrations while preserving stored procurement data. Use for persistence changes and database failures.
---

# Asuncion Database Changes

Trace the requested change through `db.py`, the affected `app.py` or `inventory_dataset.py` caller, `supabase/schema.sql`, and existing migrations. Preserve the current PostgreSQL runtime and the user's requested scope.

## Database contracts

- Set `SUPABASE_DB_URL` to an explicitly disposable PostgreSQL database before importing `app` for mutation tests. The app captures the URL at import. A filesystem DSN passed to `connect_db()` is ignored, so a temporary SQLite path is not isolation.
- `Connection.__exit__` rolls back on an exception and closes; it does not commit successful work. Use explicit `commit()` for writes. `exec_db()` and `log()` each open and commit independently: do not nest them inside an operation intended to share one transaction.
- `BEGIN IMMEDIATE` is translated to plain `BEGIN`, not a PostgreSQL row lock. For requested approval/stock fixes, lock the relevant rows, recheck status inside the transaction, and keep data/status/audit writes on that connection. Verify rollback and replay behavior.
- Before retrying an existing failed receipt, check for already committed inventory rows. A new atomic implementation does not undo earlier partial writes; reconcile affected records within the requested scope before replay.
- Preserve query parameters through the wrapper. Its legacy `?`, NOCASE, and comparison-literal translations are narrow compatibility behavior, not a complete SQLite dialect.
- Preserve one APP row per PPMP item; do not add a uniqueness constraint on `app_plan.ppmp_id`. Inspect actual parent links and existing data before adding other constraints. Sequence allocation commits independently, so gaps alone do not establish corruption.

## Schema and data changes

For a requested schema change, update the fresh-install schema and add a forward numbered migration consistent with existing migrations. Verify both a fresh database and an upgraded fixture with representative existing records. Avoid resets or legacy imports unless specifically requested.

`Connection.executescript()` splits statements at semicolons. Procedural SQL bodies cannot be inserted into the current initializer unchanged; handle their execution path explicitly if the requested migration needs them.

Inspect startup and dataset code before using a read endpoint to check a change. `init_db()` performs repairs and dataset synchronization; `inventory_dataset.ensure_schema()` also mutates metadata and drops a legacy table. HTTP or dataset-status checks require an isolated database.

Report the schema/query change, data compatibility, transaction boundary, and verification performed. Static SQL inspection is not evidence that a migration or rollback succeeded on PostgreSQL. Protect existing records and keep credentials out of patches and output.
