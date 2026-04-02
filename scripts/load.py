import duckdb
from config.config import DUCKDB_PATH, PARQUET_PATH, OUTPUT_DIR, FIELD_MAPPING


def _build_schema() -> str:
    """Build CREATE TABLE DDL from field mapping."""
    columns = []
    for key, mapping in FIELD_MAPPING.items():
        col_type = "VARCHAR"
        if mapping.get("type") == "datetime" or key in ("created",):
            col_type = "VARCHAR"  # keep as string for compatibility
        columns.append(f"    {key} {col_type}")
    return ",\n".join(columns)


def load_to_duckdb(records: list[dict]) -> None:
    """Load transformed records into DuckDB and export to Parquet."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DUCKDB_PATH))

    columns = list(FIELD_MAPPING.keys())
    schema = _build_schema()

    con.execute("DROP TABLE IF EXISTS murls")
    con.execute(f"CREATE TABLE murls (\n{schema}\n)")

    if records:
        placeholders = ", ".join(["?" for _ in columns])
        insert_sql = f"INSERT INTO murls ({', '.join(columns)}) VALUES ({placeholders})"

        rows = []
        for rec in records:
            row = tuple(rec.get(col) for col in columns)
            rows.append(row)

        con.executemany(insert_sql, rows)

    count = con.execute("SELECT count(*) FROM murls").fetchone()[0]
    print(f"Loaded {count} records into DuckDB ({DUCKDB_PATH})")

    con.execute(f"COPY murls TO '{PARQUET_PATH}' (FORMAT PARQUET)")
    print(f"Exported Parquet ({PARQUET_PATH})")

    con.close()
