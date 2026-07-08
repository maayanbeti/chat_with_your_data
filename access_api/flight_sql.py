import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from access_api.flight_rename_rows import export_to_csv_with_rename, get_column_metadata, FLIGHT_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_PATH = ROOT / "data" / "sample_flights.json"
DEFAULT_DB_PATH = ROOT / "data" / "flights.sqlite3"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS flights (
    _id INTEGER PRIMARY KEY,
    CHOPER TEXT,
    CHFLTN TEXT,
    CHOPERD TEXT,
    CHSTOL TEXT,
    CHPTOL TEXT,
    CHAORD TEXT,
    CHLOC1 TEXT,
    CHLOC1D TEXT,
    CHLOC1TH TEXT,
    CHLOC1T TEXT,
    CHLOC1CH TEXT,
    CHLOCCT TEXT,
    CHTERM REAL,
    CHCINT TEXT,
    CHCKZN TEXT,
    CHRMINE TEXT,
    CHRMINH TEXT
)
"""

INSERT_SQL = """
INSERT INTO flights (
    _id, CHOPER, CHFLTN, CHOPERD, CHSTOL, CHPTOL, CHAORD, CHLOC1,
    CHLOC1D, CHLOC1TH, CHLOC1T, CHLOC1CH, CHLOCCT, CHTERM, CHCINT,
    CHCKZN, CHRMINE, CHRMINH
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def _normalize_record(record: Dict[str, Any]) -> List[Any]:
    return [
        record.get("_id"),
        record.get("CHOPER"),
        record.get("CHFLTN"),
        record.get("CHOPERD"),
        record.get("CHSTOL"),
        record.get("CHPTOL"),
        record.get("CHAORD"),
        record.get("CHLOC1"),
        record.get("CHLOC1D"),
        record.get("CHLOC1TH"),
        record.get("CHLOC1T"),
        record.get("CHLOC1CH"),
        record.get("CHLOCCT"),
        record.get("CHTERM"),
        record.get("CHCINT"),
        record.get("CHCKZN"),
        record.get("CHRMINE"),
        record.get("CHRMINH"),
    ]


def load_flights(
    json_path: Optional[Union[Path, str]] = DEFAULT_JSON_PATH,
    db_path: Optional[Union[Path, str]] = DEFAULT_DB_PATH,
) -> Path:
    """Create a SQLite table from the flight JSON file."""
    json_path = Path(json_path)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with json_path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)

    with sqlite3.connect(db_path) as connection:
        connection.execute(CREATE_TABLE_SQL)
        connection.execute("DELETE FROM flights")
        connection.executemany(INSERT_SQL, [_normalize_record(record) for record in records])
        connection.commit()

    return db_path


def run_query(sql: str, db_path: Optional[Union[Path, str]] = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Run a read-only SQL query against the flight database."""
    db_path = Path(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(sql).fetchall()
    return [dict(row) for row in rows]


def export_flights_to_csv(
    csv_path: Optional[Union[Path, str]] = None,
    db_path: Optional[Union[Path, str]] = DEFAULT_DB_PATH,
) -> Path:
    """Export all flights to CSV with renamed columns and language metadata.
    
    Args:
        csv_path: Where to save the CSV (default: data/flights.csv)
        db_path: Path to the SQLite database
        
    Returns:
        Path to the saved CSV file
    """
    if csv_path is None:
        csv_path = Path(db_path).parent / 'flights.csv'
    
    rows = run_query('SELECT * FROM flights', db_path=db_path)
    csv_path = export_to_csv_with_rename(rows, FLIGHT_COLUMNS, csv_path)
    
    metadata = get_column_metadata(FLIGHT_COLUMNS)
    print(f'Exported {len(rows)} rows to {csv_path}')
    print('Column metadata:')
    for col, meta in metadata.items():
        lang_info = f" [{meta['language']}]" if meta['language'] else ""
        print(f"  {col}{lang_info}")
    
    return csv_path


def import_and_export_flights(
    json_path: Optional[Union[Path, str]] = DEFAULT_JSON_PATH,
    db_path: Optional[Union[Path, str]] = DEFAULT_DB_PATH,
    csv_path: Optional[Union[Path, str]] = None,
) -> Path:
    """Import flight JSON into SQLite and export a renamed CSV in one step."""
    db_path = load_flights(json_path=json_path, db_path=db_path)
    return export_flights_to_csv(csv_path=csv_path, db_path=db_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import flight data and export a renamed CSV")
    parser.add_argument("--json", default=str(DEFAULT_JSON_PATH), help="Path to the source JSON file")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="Path to the SQLite database file")
    parser.add_argument("--csv", default=str(DEFAULT_DB_PATH.parent / 'flights.csv'), help="Path to the renamed CSV output")
    parser.add_argument("--query", help="Optional SQL query to run after import")
    args = parser.parse_args()

    db_path = Path(args.db)
    csv_path = Path(args.csv)
    import_and_export_flights(json_path=args.json, db_path=db_path, csv_path=csv_path)
    print(f"Loaded flight data into {db_path}")

    if args.query:
        rows = run_query(args.query, db_path=db_path)
        if not rows:
            print("No rows returned")
        else:
            for row in rows:
                print(row)


if __name__ == "__main__":
    main()
