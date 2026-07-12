"""Mirror the flight CSV with a computed duration column.

This dataset (Ben Gurion's own flight board) never records both endpoints of
a physical flight: a "D" row is BGN's departure event (scheduled_dt/actual_dt
= BGN departure time), an "A" row is BGN's arrival event (scheduled_dt/actual_dt
= BGN arrival time), and nothing links a "D" row to a later "A" row as the same
trip. So true takeoff-to-landing flight time cannot be derived from this feed.

The only real date delta the data supports, per row, is actual_dt minus
scheduled_dt — how early/late that single BGN event was. `flight_duration_*`
below is that delta, not travel time. See .github/skills/flight-duration/SKILL.md.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = ROOT / "data" / "flights.csv"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "flights_with_duration.csv"

DT_FORMAT = "%Y-%m-%dT%H:%M:%S"


def _parse_dt(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, DT_FORMAT)
    except ValueError:
        return None


def compute_duration_rows(csv_path: Optional[Union[Path, str]] = DEFAULT_CSV_PATH) -> List[Dict[str, Any]]:
    """Read flights.csv and add flight_duration_minutes/flight_duration_days per row.

    flight_duration_minutes = actual_dt - scheduled_dt, in minutes (signed: negative
    means the event happened early). None when either timestamp is missing/unparseable.
    """
    csv_path = Path(csv_path)
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        scheduled = _parse_dt(row.get("scheduled_dt", ""))
        actual = _parse_dt(row.get("actual_dt", ""))
        if scheduled and actual:
            delta_minutes = (actual - scheduled).total_seconds() / 60
            row["flight_duration_minutes"] = round(delta_minutes, 1)
            row["flight_duration_days"] = round(delta_minutes / 1440, 3)
        else:
            row["flight_duration_minutes"] = None
            row["flight_duration_days"] = None

    return rows


def export_flights_with_duration(
    csv_path: Optional[Union[Path, str]] = DEFAULT_CSV_PATH,
    output_path: Optional[Union[Path, str]] = DEFAULT_OUTPUT_PATH,
) -> Path:
    """Write a mirrored CSV of flights.csv with the duration columns appended."""
    rows = compute_duration_rows(csv_path=csv_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        raise ValueError("No rows to export")

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return output_path
