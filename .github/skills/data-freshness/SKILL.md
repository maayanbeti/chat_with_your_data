---
name: data-freshness
description: |
  Two jobs, both built on access_api/data_freshness.py:

  1. STARTUP VALIDATION (blocking-adjacent, runs first): right after
     `clarification-flight` refreshes the live feed, run the two data-health tests —
     row count vs. the previous run, and a 20-minute freshness window — and show the
     report (last updated + both test results + overall VALID/INVALID) before the
     category question is asked.
  2. END-OF-ANSWER FOOTER (non-blocking, runs last): append a one-line "data last
     updated" footer to every answer that presents flight data results.

  Trigger phrases: no user-facing trigger question for either mode — both run
  automatically as part of the `clarification-flight` / `master-workflow` pipeline.
compatibility: |
  - Access to access_api/data_freshness.py
  - Access to data/flights.csv and/or data/flights.sqlite3
  - Write access to data/.pipeline_state.json (stores the previous run's row count
    for the row-count test)
---

# 📅 Data Freshness Skill

## Purpose

Every answer that shows numbers from the flight dataset should tell the user how
current that data is, and the pipeline should verify the data itself is healthy
before spending effort answering. This skill covers both: an upfront validation
report, and a footer at the end.

## Mode A: Startup Data-Health Validation

**Use immediately after `clarification-flight` Step 1's live refresh, before the
category question is asked.** This is a distinct check from `data-validator` — that
skill validates the *calculated answer* against the user's filters; this one
validates the *underlying data* is sane and current.

### Step 1: Run the validation

```python
from access_api.data_freshness import format_data_health_report
print(format_data_health_report())
```

which renders, e.g.:

```
📅 Data last updated: 2026-07-12T13:50:30+00:00 UTC (2858 rows)
🔢 Row count check: 2858 rows (previous run: 2846, Δ +12) — ✓ PASS
⏱️ Freshness check: refreshed 0.4 min ago (threshold: 20 min) — ✓ PASS
📊 Last read: 2,858 rows — ✅ Valid
```

The last line — `format_last_read_line()` — is the one unmissable takeaway to show the
user right after every refresh, on every question (not just the first in a session):
how many rows this run read, and a single ✅/❌ verdict. The lines above it are the
supporting detail; the last line is what a user should be able to read at a glance.

Two tests, always exactly these two:
1. **Row count check** — current row count vs. the previous run's row count,
   persisted in `data/.pipeline_state.json` (created/updated automatically). Passes
   if the current count is a real positive number. First run ever has no previous
   count to compare — that's expected, not a failure.
2. **Freshness check** — minutes since the data file was last refreshed. Passes if
   within 20 minutes. Since `clarification-flight` just refreshed the live feed in
   the previous step, this should reliably pass; it exists to catch a silent
   refresh failure.

### Step 2: Gate on the result

If `Overall` is `✓ VALID`, show the report and continue to the category question.
If `✗ INVALID`, do not proceed silently — retry the live refresh once, then either
recover to VALID or tell the user plainly what's wrong (e.g. "row count came back
as 0" or "couldn't refresh — data is over 20 minutes old") before continuing with
whatever data is available.

## Mode B: End-of-Answer Freshness Footer

**Use at the end of EVERY answer that includes flight data results** — counts,
breakdowns, charts, tables, KPIs. Runs after `data-validator` confirms VALID and
`design-output` has rendered the final chart/table/KPI.

Do **not** use it for messages that contain no data results (e.g. the clarification
form itself, error messages, or plain conversational replies).

### Step 1: Get freshness info

```python
from access_api.data_freshness import get_data_last_updated
info = get_data_last_updated()
# {"last_updated": "2026-07-12T13:50:30+00:00", "row_count": 2858, "source": "data/flights.csv"}
```

### Step 2: Format the footer

```python
from access_api.data_freshness import format_freshness_footer
print(format_freshness_footer())
# 📅 Data last updated: 2026-07-12T13:50:30+00:00 UTC (2858 rows)
```

If no data file exists, this renders `📅 Data last updated: unknown (no data file found)`.

### Step 3: Append to the answer

Add the footer as the final line of the response, separated from the main answer by
a blank line. Never block or delay the answer for this step — it is informational
only and must not gate the response the way Mode A or `data-validator` does.

## Example (full pipeline)

```
[Mode A — shown first, before the category question, on every question]
📅 Data last updated: 2026-07-12T13:50:30+00:00 UTC (2858 rows)
🔢 Row count check: 2858 rows (previous run: 2846, Δ +12) — ✓ PASS
⏱️ Freshness check: refreshed 0.4 min ago (threshold: 20 min) — ✓ PASS
📊 Last read: 2,858 rows — ✅ Valid

... category question, parameter questions, data-validator, design-output ...

[Mode B — shown last, appended to the final answer]
📊 You have 2,434 flights matching your filters (all dates, all statuses). [rendered as a chart/KPI via design-output]

📅 Data last updated: 2026-07-12T13:50:30+00:00 UTC (2,434 rows)
```

## Implementation Notes

- **Non-blocking Mode B, blocking-adjacent Mode A**: Mode A gates progress (don't ask
  the category question until it reports VALID or you've explained why not); Mode B
  never stops the flow or asks the user anything — it only adds one line at the end.
- **Source of truth**: freshness is derived from file modification time on disk, which
  reflects when `import_and_export_flights(source="live")` was last run — not from an
  `updated_at` column in the data itself. Per `clarification-flight` Step 1, that live
  refresh should have just happened moments before Mode A runs, so the timestamp
  should normally be very recent — the upstream data.gov.il feed itself updates every
  15 minutes.
- **Row-count state persists across runs**: `data/.pipeline_state.json` is written by
  `validate_data_health()` every time it runs, so the next run always has a real
  "previous run" to compare against — do not delete this file as part of a workflow.
- **Always run both modes**: apply Mode A at the start and Mode B at the end of every
  data-bearing answer, regardless of which question category (from
  `clarification-flight`) produced it.

## References
- [Python implementation](../../../access_api/data_freshness.py)
