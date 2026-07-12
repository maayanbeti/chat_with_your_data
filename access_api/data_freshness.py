"""Report when the flight dataset was last refreshed.

Used by the data-freshness skill to append a "last updated" footer to
every answer that is derived from data/flights.csv or data/flights.sqlite3,
and to run the startup data-health validation (row-count sanity vs the
previous run, and a freshness window check) before the clarification form.
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = ROOT / "data" / "flights.csv"
DEFAULT_DB_PATH = ROOT / "data" / "flights.sqlite3"
DEFAULT_STATE_PATH = ROOT / "data" / ".pipeline_state.json"
DEFAULT_FRESHNESS_THRESHOLD_MINUTES = 20


def _count_csv_rows(csv_path: Path) -> Optional[int]:
    if not csv_path.exists():
        return None
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        row_count = sum(1 for _ in csv.reader(handle)) - 1
    return max(row_count, 0)


def get_data_last_updated(
    csv_path: Optional[Union[Path, str]] = DEFAULT_CSV_PATH,
    db_path: Optional[Union[Path, str]] = DEFAULT_DB_PATH,
) -> dict:
    """Return the most recent modification time across the flight data files.

    Returns a dict with:
        last_updated: ISO-8601 UTC timestamp string, or None if no file exists
        row_count: number of data rows in the CSV, or None if unavailable
        source: path (relative to repo root) of whichever file was newest
    """
    csv_path = Path(csv_path)
    db_path = Path(db_path)

    candidates = [p for p in (csv_path, db_path) if p.exists()]
    if not candidates:
        return {"last_updated": None, "row_count": None, "source": None}

    newest = max(candidates, key=lambda p: p.stat().st_mtime)
    timestamp = datetime.fromtimestamp(newest.stat().st_mtime, tz=timezone.utc)

    return {
        "last_updated": timestamp.isoformat(timespec="seconds"),
        "row_count": _count_csv_rows(csv_path),
        "source": str(newest.relative_to(ROOT)),
    }


def format_freshness_footer(info: Optional[dict] = None) -> str:
    """Render the freshness dict as a one-line footer string."""
    info = info or get_data_last_updated()
    if not info["last_updated"]:
        return "📅 Data last updated: unknown (no data file found)"

    row_part = f" ({info['row_count']} rows)" if info["row_count"] is not None else ""
    return f"📅 Data last updated: {info['last_updated']} UTC{row_part}"


def get_available_date_range(
    csv_path: Optional[Union[Path, str]] = DEFAULT_CSV_PATH,
) -> dict:
    """Return the min/max scheduled_dt and actual_dt present in the CSV.

    Used to tell the user what date range they can actually pick in the
    clarification form's custom date-range fields.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        return {"scheduled": (None, None), "actual": (None, None)}

    scheduled_dates: list = []
    actual_dates: list = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("scheduled_dt"):
                scheduled_dates.append(row["scheduled_dt"])
            if row.get("actual_dt"):
                actual_dates.append(row["actual_dt"])

    def _bounds(values: list):
        return (min(values), max(values)) if values else (None, None)

    return {
        "scheduled": _bounds(scheduled_dates),
        "actual": _bounds(actual_dates),
    }


def format_data_context_header(
    freshness: Optional[dict] = None, date_range: Optional[dict] = None
) -> str:
    """Render the 'data context' block shown before the clarification form:
    when the data was last refreshed and what date range it covers."""
    freshness = freshness or get_data_last_updated()
    date_range = date_range or get_available_date_range()

    lines = [format_freshness_footer(freshness)]

    sched_start, sched_end = date_range["scheduled"]
    if sched_start and sched_end:
        lines.append(
            f"📊 Available dates (scheduled): {sched_start[:10]} to {sched_end[:10]}"
        )
    return "\n".join(lines)


def _load_state(state_path: Path) -> Optional[dict]:
    if not state_path.exists():
        return None
    with state_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_state(state: dict, state_path: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle)


def validate_data_health(
    freshness_threshold_minutes: int = DEFAULT_FRESHNESS_THRESHOLD_MINUTES,
    csv_path: Optional[Union[Path, str]] = DEFAULT_CSV_PATH,
    db_path: Optional[Union[Path, str]] = DEFAULT_DB_PATH,
    state_path: Optional[Union[Path, str]] = DEFAULT_STATE_PATH,
) -> dict:
    """Run the two startup data-health checks, then persist this run's stats
    as the new baseline for the next run's row-count comparison.

    Test 1 (row_count_test): current row count vs. the previous run's row
        count. Passes if the current count is a positive number — the delta
        is reported either way so a sudden drop (or a live feed refreshing
        with a few more/fewer flights) is visible.
    Test 2 (freshness_test): minutes since the data was last refreshed.
        Passes if that's within `freshness_threshold_minutes` (default 20).
    """
    state_path = Path(state_path)
    info = get_data_last_updated(csv_path=csv_path, db_path=db_path)
    current_count = info["row_count"]
    last_updated = info["last_updated"]

    previous = _load_state(state_path)
    previous_count = previous.get("row_count") if previous else None

    delta = None
    if current_count is not None and previous_count is not None:
        delta = current_count - previous_count

    row_count_test = {
        "current_count": current_count,
        "previous_count": previous_count,
        "delta": delta,
        "passed": current_count is not None and current_count > 0,
    }

    minutes_since_update = None
    freshness_passed = False
    if last_updated:
        updated_dt = datetime.fromisoformat(last_updated)
        minutes_since_update = (datetime.now(timezone.utc) - updated_dt).total_seconds() / 60
        freshness_passed = minutes_since_update <= freshness_threshold_minutes

    freshness_test = {
        "minutes_since_update": minutes_since_update,
        "threshold_minutes": freshness_threshold_minutes,
        "passed": freshness_passed,
    }

    overall = "VALID" if (row_count_test["passed"] and freshness_test["passed"]) else "INVALID"

    _save_state({"row_count": current_count, "last_updated": last_updated}, state_path=state_path)

    return {
        "row_count_test": row_count_test,
        "freshness_test": freshness_test,
        "overall": overall,
    }


def format_last_read_line(result: Optional[dict] = None) -> str:
    """Render the one-line, unmissable summary shown after every refresh:
    how many rows this run read, and whether the data-health check passed.

    This is the line to show the user right after the live refresh, before
    the clarification follow-up question and before any output — a single
    clear signal, not the full multi-line report.
    """
    result = result or validate_data_health()
    count = result["row_count_test"]["current_count"]
    count_str = f"{count:,}" if count is not None else "unknown"
    is_valid = result["overall"] == "VALID"
    return f"📊 Last read: {count_str} rows — {'✅ Valid' if is_valid else '❌ Invalid'}"


def format_data_health_report(result: Optional[dict] = None) -> str:
    """Render the startup data-health check (last updated + 2 tests + the
    clear last-read-line) as text."""
    result = result or validate_data_health()
    rc = result["row_count_test"]
    ft = result["freshness_test"]

    lines = [format_freshness_footer()]

    if rc["previous_count"] is not None:
        sign = "+" if (rc["delta"] or 0) >= 0 else ""
        lines.append(
            f"🔢 Row count check: {rc['current_count']} rows "
            f"(previous run: {rc['previous_count']}, Δ {sign}{rc['delta']}) — "
            f"{'✓ PASS' if rc['passed'] else '✗ FAIL'}"
        )
    else:
        lines.append(
            f"🔢 Row count check: {rc['current_count']} rows "
            f"(no previous run recorded yet) — {'✓ PASS' if rc['passed'] else '✗ FAIL'}"
        )

    if ft["minutes_since_update"] is not None:
        lines.append(
            f"⏱️ Freshness check: refreshed {ft['minutes_since_update']:.1f} min ago "
            f"(threshold: {ft['threshold_minutes']} min) — "
            f"{'✓ PASS' if ft['passed'] else '✗ FAIL'}"
        )
    else:
        lines.append("⏱️ Freshness check: unknown (no timestamp) — ✗ FAIL")

    lines.append(format_last_read_line(result))
    return "\n".join(lines)
