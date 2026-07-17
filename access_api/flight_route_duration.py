"""Estimate flight duration by destination country.

`flights.csv` never records both ends of a single physical flight (see
`.github/skills/flight-duration/SKILL.md`), so there is no way to *measure*
true takeoff-to-landing time from this dataset. This module instead attaches
a **published/typical average flight time** per destination country as a
reference column, so "shortest/longest flight" questions can be answered
against an estimate rather than left unanswerable.

`AVG_FLIGHT_HOURS_BY_COUNTRY` values are commonly published average
non-stop flight durations between Tel Aviv (Ben Gurion) and that country's
airport(s) served in this dataset. They are approximations, not derived from
`flights.csv` timestamps, and are not flight-specific (a country with
multiple destination cities uses one representative average). See
`.github/skills/flight-route-duration/SKILL.md`.
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = ROOT / "data" / "flights.csv"
DEFAULT_COUNTRY_CSV_PATH = ROOT / "data" / "country_avg_flight_duration.csv"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "flights_with_route_duration.csv"

# Typical average one-way flight duration (hours) from Tel Aviv (BGN) to each
# destination country present in this dataset. Approximate reference values,
# not measured from flight_status data.
AVG_FLIGHT_HOURS_BY_COUNTRY: Dict[str, float] = {
    "ALBANIA": 2.0,
    "ARMENIA": 2.0,
    "AUSTRIA": 3.5,
    "AZERBAIJAN": 2.75,
    "BELARUS": 3.5,
    "BELGIUM": 4.5,
    "BOSNIA": 2.75,
    "BULGARIA": 2.0,
    "CROATIA": 2.75,
    "CYPRUS": 1.0,
    "CZECH REPUBLIC": 3.75,
    "DENMARK": 4.5,
    "ETHIOPIA": 4.5,
    "FRANCE": 4.5,
    "GEORGIA": 2.75,
    "GERMANY": 4.25,
    "GREECE": 1.75,
    "HUNGARY": 3.0,
    "ICELAND": 6.5,
    "ISRAEL": 1.0,
    "ITALY": 3.75,
    "JAPAN": 11.5,
    "LATVIA": 4.25,
    "LITHUANIA": 4.0,
    "MOLDOVA": 2.25,
    "MONTENEGRO": 2.75,
    "NETHERLANDS": 4.75,
    "POLAND": 3.75,
    "PORTUGAL": 5.75,
    "ROMANIA": 2.5,
    "RUSSIAN FEDERATION": 4.0,
    "SERBIA": 2.75,
    "SLOVAKIA": 3.5,
    "SLOVENIA": 3.25,
    "SPAIN": 5.0,
    "SWITZERLAND": 4.25,
    "TANZANIA": 6.5,
    "THAILAND": 9.5,
    "UNITED ARAB EMIRATES": 3.25,
    "UNITED KINGDOM": 5.0,
    "UNITED STATES": 11.5,
    "UZBEKISTAN": 3.5,
}


def export_country_avg_duration(
    output_path: Optional[Union[Path, str]] = DEFAULT_COUNTRY_CSV_PATH,
) -> Path:
    """Write the country -> avg_flight_hours reference table as a CSV."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["destination_country_en", "avg_flight_hours_estimate"])
        for country in sorted(AVG_FLIGHT_HOURS_BY_COUNTRY):
            writer.writerow([country, AVG_FLIGHT_HOURS_BY_COUNTRY[country]])

    return output_path


def compute_route_duration_rows(
    csv_path: Optional[Union[Path, str]] = DEFAULT_CSV_PATH,
) -> List[Dict[str, Any]]:
    """Read flights.csv and attach avg_flight_hours_estimate per row.

    Looked up by destination_country_en. None when the country has no
    reference entry (unmapped destination).
    """
    csv_path = Path(csv_path)
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        country = (row.get("destination_country_en") or "").strip()
        row["avg_flight_hours_estimate"] = AVG_FLIGHT_HOURS_BY_COUNTRY.get(country)

    return rows


def export_flights_with_route_duration(
    csv_path: Optional[Union[Path, str]] = DEFAULT_CSV_PATH,
    output_path: Optional[Union[Path, str]] = DEFAULT_OUTPUT_PATH,
) -> Path:
    """Write a mirrored CSV of flights.csv with avg_flight_hours_estimate appended.

    Skips the rewrite (cache hit) when `output_path` already exists and is
    newer than `csv_path` — the mirror is a pure function of its source, so
    there's nothing new to compute until `flights.csv` is refreshed again.
    """
    csv_path = Path(csv_path)
    output_path = Path(output_path)
    if output_path.exists() and output_path.stat().st_mtime >= csv_path.stat().st_mtime:
        return output_path

    rows = compute_route_duration_rows(csv_path=csv_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        raise ValueError("No rows to export")

    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    return output_path
