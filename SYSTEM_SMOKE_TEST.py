"""Non-destructive readiness test for the Supabase-based PSMS build."""
from pathlib import Path
import sys

from db import ping, connect_db
from aoq_flexible import extract_document

ROOT = Path(__file__).resolve().parent


def check(name, condition, detail=""):
    if not condition:
        raise RuntimeError(f"FAIL: {name}: {detail}")
    print(f"PASS: {name}")


def main():
    check("Supabase/PostgreSQL connection", ping(), "start local Supabase first")
    with connect_db() as con:
        required = ["ppmp", "app_plan", "pr", "aoq", "po", "nlp", "iar", "inventory", "ris_ics", "audit_trail", "users"]
        rows = con.execute("select tablename from pg_tables where schemaname='public'").fetchall()
        present = {r["tablename"] for r in rows}
        missing = [t for t in required if t not in present]
        check("required database tables", not missing, missing)
        count = con.execute("select count(*) as c from users").fetchone()["c"]
        check("administrator/user table initialized", count >= 1, count)

    sample = ROOT / "sample_files" / "SAMPLE_AOQ_ONE_WINNER.xlsx"
    result = extract_document(str(sample))
    check("office-document extraction", bool(result.get("raw_text")), result.get("warnings"))
    print("All non-destructive smoke tests passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(exc)
        raise SystemExit(1)
