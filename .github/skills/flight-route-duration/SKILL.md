---
name: flight-route-duration
description: |
  Use this skill whenever a user asks which flight is "shorter"/"longer"/
  "shortest"/"longest" **in the air** (true flight time, not schedule
  deviation/delay). `flights.csv` cannot measure this directly — see
  `.github/skills/flight-duration/SKILL.md` for why. Instead, attach a
  published/typical average flight-time-per-destination-country reference
  column (`avg_flight_hours_estimate`) via `access_api/flight_route_duration.py`,
  and answer from that mirrored file.

  Trigger phrases: "shorter flight" / "longer flight" / "shortest flight" /
  "longest flight" when the user confirms they mean true flight time (not
  delay) — e.g. after clarifying that the dataset only has departure OR
  arrival timestamps per row, never both, for the same physical trip.
compatibility: |
  - Access to data/flights.csv (refreshed by clarification-flight Step 1)
  - access_api/flight_route_duration.py (AVG_FLIGHT_HOURS_BY_COUNTRY,
    export_country_avg_duration, export_flights_with_route_duration)
---

# 🛫 Flight Route Duration (Estimate) Skill

## Purpose

`flights.csv` records only one BGN-side event per row (a departure OR an
arrival), never both ends of the same physical trip — see the critical data
limitation in `.github/skills/flight-duration/SKILL.md`. That skill answers
"duration" as schedule deviation (`actual_dt - scheduled_dt`), which is
delay/earliness, not travel time.

When the user explicitly wants true flight time instead (confirmed after
being told the delay-vs-travel-time distinction), this skill provides the
next best thing: a **country-level average flight-time reference**, sourced
from commonly published typical non-stop flight durations between Tel Aviv
(Ben Gurion) and each destination country — not measured from this dataset.

**Always tell the user this is an estimate**, not a per-flight measurement:
every flight to the same country gets the same `avg_flight_hours_estimate`
value regardless of aircraft, route, or wind conditions on that specific day.

## How to Use This Skill

### Step 1: Build/refresh the reference table

```python
from access_api.flight_route_duration import export_country_avg_duration
export_country_avg_duration()  # writes data/country_avg_flight_duration.csv
```

This writes a two-column CSV: `destination_country_en`, `avg_flight_hours_estimate`.

### Step 2: Mirror flights.csv with the estimate joined in

```python
from access_api.flight_route_duration import export_flights_with_route_duration
export_flights_with_route_duration()  # writes data/flights_with_route_duration.csv
```

Run this after `data/flights.csv` has been refreshed live (per
`clarification-flight` Step 1) — the join is looked up by
`destination_country_en` against `AVG_FLIGHT_HOURS_BY_COUNTRY` in
`access_api/flight_route_duration.py`. A country with no reference entry gets
`None` for `avg_flight_hours_estimate` — do not treat `None` as zero.

### Step 3: Answer from the mirrored file

Use `data/flights_with_route_duration.csv` for "shortest/longest flight in
the air" questions:
- **Shortest** = `min(avg_flight_hours_estimate)` among the flights in scope
  (after clarification-flight's filters) → e.g. Cyprus at 1.0h.
- **Longest** = `max(avg_flight_hours_estimate)` among the flights in scope
  → e.g. Japan or United States at 11.5h.

State the country (and the specific flight rows that go there), the estimated
hours, and explicitly label it: "estimated typical flight time for this
route, not measured from this flight's actual timestamps."

### Step 4: Follow the rest of the pipeline as normal

Still run `data-validator` (recheck the min/max against
`flights_with_route_duration.csv`) and `design-output` (render as
chart/table/KPI) before presenting the answer, and still append the
`data-freshness` footer.

## Implementation Notes

- `access_api/flight_route_duration.py`:
  - `AVG_FLIGHT_HOURS_BY_COUNTRY`: dict of country -> avg hours (edit this to
    refine estimates or add newly-seen destination countries).
  - `export_country_avg_duration()`: writes the reference CSV.
  - `compute_route_duration_rows()` / `export_flights_with_route_duration()`:
    join the estimate onto `flights.csv` rows.
- If a destination country appears in `flights.csv` but not in
  `AVG_FLIGHT_HOURS_BY_COUNTRY`, add it there first — do not guess inline.
- This skill is a superset companion to `.github/skills/flight-duration/SKILL.md`,
  not a replacement — use `flight-duration` for schedule-deviation/delay
  questions, and this skill for true-flight-time questions.

## References
- [Python implementation](../../../access_api/flight_route_duration.py)
- [Schedule-deviation duration skill](../flight-duration/SKILL.md)
