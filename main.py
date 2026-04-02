import argparse
import json
from pathlib import Path

from config.config import OUTPUT_DIR, JIRA_TOKEN, RAW_CACHE_PATH
from scripts.extract import extract_all, load_cache
from scripts.transform import transform_all
from scripts.load import load_to_duckdb
from scripts.report import generate_report


def run_extract(limit: int | None = None, resume: bool = False) -> list[dict]:
    print("=" * 50)
    print("STEP 1: Extract from Jira API")
    print("=" * 50)
    return extract_all(limit=limit, resume=resume)


def run_transform(raw: list[dict] | None = None) -> list[dict]:
    print("=" * 50)
    print("STEP 2: Transform")
    print("=" * 50)
    if raw is None:
        raw = load_cache()
        print(f"Loaded {len(raw)} records from cache")
    return transform_all(raw)


def run_load(records: list[dict]) -> None:
    print("=" * 50)
    print("STEP 3: Load to DuckDB + Parquet")
    print("=" * 50)
    load_to_duckdb(records)


def run_report(records: list[dict] | None = None) -> None:
    print("=" * 50)
    print("STEP 4: Generate XLSX Report")
    print("=" * 50)
    if records is None:
        import duckdb
        from config.config import DUCKDB_PATH, FIELD_MAPPING
        con = duckdb.connect(str(DUCKDB_PATH))
        columns = list(FIELD_MAPPING.keys())
        rows = con.execute(f"SELECT {', '.join(columns)} FROM murls").fetchall()
        records = [dict(zip(columns, row)) for row in rows]
        con.close()
        print(f"Loaded {len(records)} records from DuckDB")
    generate_report(records)


def main():
    parser = argparse.ArgumentParser(description="MURL Data Pipeline")
    parser.add_argument("--step", choices=["extract", "transform", "load", "report"],
                        help="Run a specific step only")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of records to extract (for testing)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume extraction from cached data after a failure")
    args = parser.parse_args()

    if not JIRA_TOKEN:
        print("Error: JIRA_TOKEN not set. Copy .env.example to .env and fill in your token.")
        return

    if args.step == "extract":
        run_extract(limit=args.limit, resume=args.resume)
    elif args.step == "transform":
        records = run_transform()
        print(f"Result: {len(records)} records (not loaded)")
    elif args.step == "load":
        records = run_transform()
        run_load(records)
    elif args.step == "report":
        run_report()
    else:
        raw = run_extract(limit=args.limit, resume=args.resume)
        records = run_transform(raw)
        run_load(records)
        run_report(records)

    print("\nDone.")


if __name__ == "__main__":
    main()
