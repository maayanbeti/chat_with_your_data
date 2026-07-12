---
name: flight-duration
description: |
  Use this skill whenever a user asks about flight "duration", "how long", or
  which flight is "shorter"/"longer"/"shortest"/"longest" in time. This dataset
  cannot answer that as true takeoff-to-landing travel time — see the caveat
  below. Instead, mirror `data/flights.csv` with a computed
  `flight_duration_minutes` / `flight_duration_days` column (actual_dt minus
  scheduled_dt, per row) via `access_api/flight_duration.py`, and answer using
  that mirrored file.

  Trigger phrases: "shorter flight", "longer flight", "shortest flight",
  "longest flight", "flight duration", "how long is/was flight X", "which
  flight took the longest/shortest".
compatibility: |
  - Access to data/flights.csv (refreshed by clarification-flight Step 1)
  - access_api/flight_duration.py (compute_duration_rows, export_flights_with_duration)
---

# ⏱️ Flight Duration Skill

## Purpose

Define what "flight duration" means for this dataset, and how to compute it,
so every future duration/shorter/longer question is answered consistently
instead of guessed at per-conversation.

## Critical data limitation — read this first

Ben Gurion's flight board (`data/flights.csv`) records **one endpoint per
row**, tagged by `departure_ind`:

- `D` rows: BGN is the **origin**. `scheduled_dt`/`actual_dt` are BGN's
  departure time; `destination_*` is where the flight is going.
- `A` rows: BGN is the **destination**. `scheduled_dt`/`actual_dt` are BGN's
  arrival time; `destination_*` is actually where the flight came **from**.

No row carries both a takeoff time and a landing time for the same physical
flight, and `D`/`A` rows are not reliably paired by `flight_num` into a single
trip. **True takeoff-to-landing flight time cannot be computed from this
data.** Do not attempt to match a `D` row to a later `A` row to estimate travel
time — there is no confirmed pairing logic for that in this feed.

## What "duration" means here instead

The only real date delta this data supports, per row, is:

```
flight_duration_minutes = actual_dt - scheduled_dt   (in minutes, signed)
flight_duration_days    = flight_duration_minutes / 1440
```

This is **the delay/earliness of that single BGN event** (how far the actual
time drifted from the scheduled time) — not how long the flight was in the
air. Always state this distinction to the user when answering a duration
question; never present it as real flight travel time.

## How to Use This Skill

### Step 1: Mirror the dataset with the duration column

```python
from access_api.flight_duration import export_flights_with_duration
export_flights_with_duration()  # writes data/flights_with_duration.csv
```

Run this after `data/flights.csv` has been refreshed live (per
`clarification-flight` Step 1) — the mirror is derived from whatever CSV is
currently on disk.

### Step 2: Answer from the mirrored file

Use `data/flights_with_duration.csv` (not `flights.csv`) for any "shorter",
"longer", "shortest", "longest", or "duration" question — e.g. shortest =
`min(abs(flight_duration_minutes))` won't make sense as "shortest flight"
without also stating the delay-vs-travel-time caveat; prefer surfacing it as
"the flight with the smallest/largest schedule deviation" rather than implying
travel time.

### Step 3: Follow the rest of the pipeline as normal

This skill only changes which file backs the calculation. Still run
`data-validator` (recount against `flights_with_duration.csv`) and
`design-output` (render as chart/table/KPI) as usual before presenting the
answer, and still append the `data-freshness` footer.

## Implementation Notes

- `access_api/flight_duration.py`: `compute_duration_rows()` returns the rows
  in memory; `export_flights_with_duration()` writes the mirrored CSV to
  `data/flights_with_duration.csv`.
- Rows with a missing/unparseable `scheduled_dt` or `actual_dt` get `None` for
  both duration columns — do not treat `None` as zero.
- If a user's phrasing implies true flight travel time (e.g. "how long does it
  take to fly to Athens"), tell them this data can't answer that, rather than
  silently substituting the delay metric without saying so.

## References
- [Python implementation](../../../access_api/flight_duration.py)
