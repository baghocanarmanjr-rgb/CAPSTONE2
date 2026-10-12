"""PostgreSQL/Supabase database access for the PSMS application.

The application uses the PostgreSQL database that backs Supabase.  For the
municipality's offline-first deployment, point ``SUPABASE_DB_URL`` at a local
Supabase instance (recommended).  The same code also works with a hosted
Supabase Postgres connection string when internet access is available.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Iterable

import psycopg
from psycopg.rows import dict_row

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LOCAL_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"


def database_url() -> str:
    return os.environ.get("SUPABASE_DB_URL", DEFAULT_LOCAL_URL).strip()


def _translate_sql(sql: str) -> str:
    """Translate the small amount of legacy SQLite-flavoured SQL still used by routes.

    This is intentionally narrow: parameter markers, NOCASE sorting, BEGIN IMMEDIATE,
    and double-quoted string literals from the legacy code.  Schema creation itself is
    PostgreSQL-native and lives in ``supabase/schema.sql``.
    """
    sql = str(sql)
    sql = re.sub(r"\bbegin\s+immediate\b", "BEGIN", sql, flags=re.I)
    sql = re.sub(r"\s+collate\s+nocase\b", "", sql, flags=re.I)
    # Legacy route SQL used SQLite's permissive status="Value" style. PostgreSQL
    # treats double quotes as identifiers, so normalize only comparison literals.
    sql = re.sub(
        r'([=<>])\s*"([^"\n]*)"',
        lambda m: f"{m.group(1)} '{m.group(2).replace(chr(39), chr(39) * 2)}'",
        sql,
    )
    sql = sql.replace("?", "%s")
    return sql


class Connection:
    def __init__(self, dsn: str | None = None):
        self._con = psycopg.connect(dsn or database_url(), row_factory=dict_row)

    def execute(self, sql: str, params: Iterable[Any] = ()):
        return self._con.execute(_translate_sql(sql), tuple(params))

    def executescript(self, script: str):
        """Execute a PostgreSQL schema script statement-by-statement.

        The project schema contains plain DDL only (no procedural bodies), so a
        semicolon split is deterministic and avoids driver multi-statement mode.
        """
        result = None
        for statement in str(script).split(';'):
            statement = statement.strip()
            if not statement or statement.startswith('--') and '\n' not in statement:
                continue
            result = self._con.execute(statement)
        return result

    def commit(self) -> None:
        self._con.commit()

    def rollback(self) -> None:
        self._con.rollback()

    def close(self) -> None:
        self._con.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.rollback()
        self.close()


def connect_db(dsn: str | None = None) -> Connection:
    # ``dsn`` is kept for compatibility with inventory_dataset.py.  A filesystem
    # path is intentionally ignored; this build has no SQLite runtime.
    target = dsn if dsn and str(dsn).startswith(("postgres://", "postgresql://")) else None
    return Connection(target)


def ping() -> bool:
    try:
        with connect_db() as con:
            row = con.execute("select 1 as ok").fetchone()
            return bool(row and row.get("ok") == 1)
    except Exception:
        return False


def apply_schema() -> None:
    schema_path = BASE_DIR / "supabase" / "schema.sql"
    script = schema_path.read_text(encoding="utf-8")
    with connect_db() as con:
        con.executescript(script)
        con.commit()
