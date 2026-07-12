---
name: clarification-flight
description: |
  Use this skill EVERY TIME a user asks a question about flight data. Before answering any flight-related query, present an interactive dropdown asking WHICH KIND of question this is, then reveal the matching parameter fields for that category and collect them.

  Trigger phrases: "how many flights", "which flights", "flight statistics", "flight data", "flights with", "count of flights", "tell me about flights", or ANY question about flight information.

  The skill presents a category dropdown (with icons) — Total Count, Flight Status, Destination/Country, Airline, Date Range, or Custom — and then a parameter form scoped to that category (dates, statuses, destination, airline, or free text). User selections determine which flights to analyze in the response.
compatibility: |
  - Network access to the live data.gov.il datastore API via access_api/flight_sql.py
    (import_and_export_flights(source="live")) — always refresh before answering
  - Access to flight data (CSV file with columns: airline_code, airline_name, scheduled_dt, actual_dt, departure_ind, destination_airport_code/name, destination_city/country, flight_status_en)
  - Access to access_api/data_freshness.py (data context header + validate_data_health
    startup check + row-count/freshness state persisted in data/.pipeline_state.json)
  - An in-chat interactive-question mechanism (e.g. AskUserQuestion) for the category
    dropdown and other fixed-choice fields; plain chat text for free-form values (dates,
    typed destination/airline/custom filter text)
  - access_api/design_output.py (every answer's final output must be rendered as a
    chart/table/KPI via the design-output skill, never plain unstyled text)
---

# ✈️ Flight Data Clarification Skill

## Purpose

Before answering ANY question about flight data, first show the user the **data
context** (when the data was last refreshed, what date range it covers), then ask
**what kind of question** this is via an in-chat interactive form — a dropdown with
icons plus real date values — and collect only the parameters relevant to that
category. Everything happens directly in the conversation; never send the user to
an external link or page to interact with the form. This keeps the form short and
focused instead of always showing every possible filter, while still covering the
full range of things people ask about this dataset (not just dates and status).

## When to Use This Skill

**Use this skill for EVERY flight data question**, including:
- "How many flights do we have?"
- "Show me flight statistics"
- "Which flights arrived on time?"
- "How many flights departed yesterday?"
- "How many flights to Larnaca?"
- "Which airline has the most flights?"
- "How many flights were cancelled this week?"
- Any other flight-related analysis or counting query

**CRITICAL: The skill runs BEFORE answering. NO answer is provided until the form is submitted.**

---

## How It Works

### Step 1: Refresh From the Live Feed, Then Show the Data Context

Before anything else, refresh the local data from the live data.gov.il flight
feed — never answer from a stale local snapshot:

```python
from access_api.flight_sql import import_and_export_flights
import_and_export_flights(source="live")
```

This pulls the current Ben Gurion flight board (data.gov.il resource
`e83f763b-b7d7-479e-b172-ae981ddc6de5`, which the source itself refreshes every
15 minutes), replacing `data/flights.sqlite3` and `data/flights.csv`. Only fall
back to the static `data/sample_flights.json` (`source="json"`) if the live
fetch fails (e.g. no network) — and say so explicitly to the user if you do.

Then show two lines sourced from `access_api/data_freshness.py`:

```python
from access_api.data_freshness import format_data_context_header
print(format_data_context_header())
```

which renders, e.g.:

```
📅 Data last updated: 2026-07-12T13:50:30+00:00 UTC (2858 rows)
📊 Available dates (scheduled): 2026-07-11 to 2026-07-15
```

This tells the user how fresh the data is and what date range they can actually
pick before they see the date fields — do this for every question, every time,
even if the user doesn't ask about freshness.

### Step 2: Run the Data-Health Validation (2 tests)

Immediately after the data context, run the startup validation from
`access_api/data_freshness.py` and show its report **before** asking anything else:

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

The final line (`format_last_read_line()`) is the unmissable, at-a-glance verdict —
show it every time, on every question, right after the refresh and before the
category question below. If `Overall`/this line reports Invalid, do not proceed —
see Step 2 below.

This runs exactly **two tests** every time, before the category question:
1. **Row count check** — current row count vs. the previous run's row count
   (persisted in `data/.pipeline_state.json`, updated on every call). Passes if
   the current count is a real positive number; the delta is shown either way
   so a live-feed fluctuation (a few flights added/removed) is visible, and a
   sudden drop to 0 stands out.
2. **Freshness check** — minutes since the data was last refreshed. Passes if
   that's within 20 minutes (it should be, immediately after Step 1's live
   refresh — this test mainly guards against Step 1 silently failing).

If `Overall` is `✗ INVALID`, do not proceed — retry the live refresh once, and
if it's still invalid, tell the user plainly what failed (e.g. "row count came
back as 0" or "couldn't refresh — data is over 20 minutes old") before
continuing with whatever data is available.

### Step 3: Display Introduction Message

Right after the data-health report, add:

> "Thank you for asking, we would like to clarify a few things before answering."

Then immediately present the interactive form (see below), inline in the chat.
**STOP - do not answer the question yet.**

### Step 4: Present the Question-Category Dropdown 🔽 (in-chat)

Present the category choice using the chat's native interactive-question mechanism
(e.g. `AskUserQuestion`), never an externally-hosted form — the user selects by
clicking, right where they're already talking to you.

**Question:** "What would you like to know?"

Options, each shown with an icon:

| Icon | Category | Use for questions about... |
|------|----------|------------------------------|
| 🔢 | Total Count | Overall flight totals ("how many flights") |
| ✈️ | Flight Status | landed / delayed / cancelled / scheduled / on-time counts |
| 🌍 | Destination / Country | flights to a specific city, airport, or country |
| 🏢 | Airline | flights by a specific carrier |
| 📅 | Date Range | flights within a scheduled/actual date window, no other filter |
| 🔍 | Custom / Other | anything not covered above |

The dropdown starts unset ("Select a category…"); the parameter fields below only
appear once a category is chosen (progressive disclosure).

### Step 5: Ask the Category's Parameter Questions (in-chat)

Ask only the questions for the chosen category, using `AskUserQuestion` for
fixed choices and plain chat text for free-form values (dates, typed names):

#### 🔢 Total Count
- Choice: "All dates" / "Custom range" → if custom, ask (plain text) for scheduled-date start/end, reminding the user of the available range from Step 1
- Optional: Flight Status multi-select (defaults to all statuses if none picked)

#### ✈️ Flight Status
- Multi-select: any number of ☑ 🛬 landed ☑ 🛫 departed ☑ ❌ cancelled ☑ ✅ on time ☑ ⏳ not final ☑ ⏰ delayed ☑ 📍 landing ☑ 🎯 final ☑ ⚡ early
  - Default: if none selected, ALL statuses included
- Date range: "All dates" / "Custom range" (plain-text start/end if custom)

#### 🌍 Destination / Country
- Plain text: destination city, airport, or country (matches `destination_city_en`, `destination_airport_name`, or `destination_country_en`)
- Date range: "All dates" / "Custom range"

#### 🏢 Airline
- Plain text: airline name or code (matches `airline_name` or `airline_code`)
- Date range: "All dates" / "Custom range"

#### 📅 Date Range
- Choice: which date field — "Scheduled" / "Actual"
- Plain text: start date, end date (within the available range from Step 1)

#### 🔍 Custom / Other
- Plain text: user describes the filter in their own words (e.g. "flights with a terminal number")
- Date range: "All dates" / "Custom range"

Dates are always real values the user types or picks (e.g. from a real date field if
the surface supports one) within the available range shown in Step 1 — never a preset
multiple-choice list of ranges standing in for an arbitrary date.

### Step 6: Confirm Selections

Once every question for the category has been answered, show a short confirmation
summarizing the chosen category and all parameter values:

> "✓ Selections received — Category = [icon] [category], [param]: [value], Dates: [range]"

Then extract:
1. The chosen category (Total Count / Flight Status / Destination / Airline / Date Range / Custom)
2. The parameter values entered for that category
3. Any date range specified

### Step 7: WAIT for All Answers

**BLOCKING STEP:** Do NOT answer the original question until every parameter question
for the chosen category has been answered and the confirmation summary has been shown.

### Step 8: Answer the Question Based on Form Selections

ONLY AFTER the user clicks OK and selections are confirmed, calculate using ONLY the
flights that match the category's filters, e.g. for Destination/Country:

```
Filtered flights = All flights WHERE
  (destination_city_en OR destination_airport_name OR destination_country_en) MATCHES destination_value
  AND (scheduled_dt BETWEEN start AND end OR date_range = "all")
```

Then, in order:
1. Hand off to `data-validator` (recount + confirm VALID before showing anything).
2. Hand off to `design-output` — the final output is **always** rendered as a
   chart/table/KPI via `access_api/design_output.py`, never a bare sentence with just
   a number. Even a single total-count answer gets a KPI card treatment.
3. Include the filter summary for clarity: "Based on your selections (category:
   [category], [param]: [value], dates: [range]), you have [COUNT] flights."
4. Hand off to `data-freshness` (append the "data last updated" footer) last.

---

## Visual Design & UX

### Styling & Emojis
- Use clear, friendly language
- Include the category icon in the dropdown options and again in the confirmation message
- Recommend the category that best matches the user's original wording (mark it "(Recommended)"), but still require an explicit pick

### Question Flow (in-chat)
- Category question always asked first, alone
- Parameter questions for that category are asked right after, one `AskUserQuestion` call per fixed-choice field, plain text for free-form values
- If the user picks a different category mid-flow, drop the previous category's partial answers and ask that new category's questions instead
- Confirmation summary shown once all parameter questions for the category are answered

### Interactive Behavior
- Parameter questions only asked after a category is chosen (progressive disclosure)
- Custom-range date questions only asked when "Custom range" is chosen (nested progressive disclosure)
- Status multi-select defaults to "all" if the user picks none

---

## Example Flow

```
👤 User: "How many flights to Cyprus do we have?"

🤖 Claude: [refreshes from the live feed first: `import_and_export_flights(source="live")`]
   📅 Data last updated: 2026-07-12T13:50:30+00:00 UTC (2858 rows)
   📊 Available dates (scheduled): 2026-07-11 to 2026-07-15

   [runs the data-health validation]
   🔢 Row count check: 2858 rows (previous run: 2846, Δ +12) — ✓ PASS
   ⏱️ Freshness check: refreshed 0.4 min ago (threshold: 20 min) — ✓ PASS
   📊 Last read: 2,858 rows — ✅ Valid

   "Thank you for asking, we would like to clarify a few things before answering."
   [AskUserQuestion: "What would you like to know?" — 🔢 Total Count | ✈️ Flight Status | 🌍 Destination/Country | 🏢 Airline | 📅 Date Range | 🔍 Custom]
   [WAITING - no answer yet]

👤 User picks: 🌍 Destination / Country

🤖 [Plain text] "Which destination (city, airport, or country)?"
   [AskUserQuestion] "All dates or a custom range?"

👤 User answers:
   - Destination: "Cyprus"
   - Dates: All dates

🤖 Confirmation: "✓ Selections received — Category = 🌍 Destination/Country | Destination = Cyprus | Dates = all"

📊 Claude responds (after data-validator confirms VALID, then design-output renders a KPI card):
   "Based on your selections (category: Destination/Country, destination: Cyprus,
    dates: all), you have 14 flights. [rendered as a KPI card, not just this sentence]

    📅 Data last updated: 2026-07-12T13:50:30+00:00 UTC (2858 rows)"
```

---

## Key Behavior: Blocking Form

**The form is ALWAYS asked first, in-chat. The answer ONLY comes after every question is answered.**

- User asks any flight question → live refresh runs → data-health validation (2 tests) shown → category question appears, in-chat
- NO answer is given while the form is still being asked
- User picks a category → matching parameter questions are asked → user answers them
- Confirmation shown → data-validator runs → design-output renders a chart/table/KPI → data-freshness footer appended
- If user asks another flight question → the whole flow (refresh, validation, category question) runs again

---

## Implementation Notes

**CRITICAL RULE:** This skill MUST run and be COMPLETED before answering ANY flight question.

- **Always refresh from the live feed first**: call
  `import_and_export_flights(source="live")` before anything else, every time — never
  answer from a local CSV/SQLite snapshot that could be stale. Only fall back to the
  static sample JSON if the live fetch errors, and tell the user you did.
- **Data context always first**: call `format_data_context_header()` (after the live
  refresh) and show its two lines before the intro sentence and before the form, every
  time — no exceptions.
- **Then validate data health (2 tests)**: call `format_data_health_report()` right
  after the data context — row-count check vs. the previous run, and a 20-minute
  freshness check. Show the report and confirm `Overall: ✓ VALID` before asking the
  category question. This is a distinct check from `data-validator` (which validates
  the *calculated answer*, not the underlying data's health).
- **Blocking behavior**: Ask the category question and its parameter questions, then
  WAIT. No answer text until every question is answered.
- **Every flight question triggers this form**: "how many flights", "flights to X", "flight count", "which airline", etc. — ALL require the form first.
- **Stay inline in the chat — never send the user to an external link.** Do not use
  the Artifact tool (or any tool that publishes to an external URL) for this form. All
  interaction — category selection, parameters, dates — must happen directly in the
  conversation the user is already in.
- **Category and single/multi-select choices** (category dropdown, status checklist,
  destination/airline pick-from-list, "all dates vs custom range"): use the chat's
  native interactive-question mechanism (e.g. `AskUserQuestion`) so the user picks by
  clicking, with icons in the option labels.
- **Free-form values that aren't a fixed choice** (an actual start/end date, a typed
  destination or airline name, a custom free-text filter): ask directly in plain chat
  text instead of forcing a preset multiple-choice list — a real calendar date can't be
  enumerated as 2-4 options. Mention the available date range (from Step 1) so the user
  knows what's valid to type.
- If the user asks a question that clearly maps to one category, mark that option
  "(Recommended)" in the category question for convenience, but the user must still
  make an explicit pick.
- Always show the chosen category and filters in your final answer for transparency
- Show a confirmation message once every question is answered (e.g., "✓ Selections received: Category = ✈️ Flight Status, Statuses = all, Dates = all")
- **Full order, every time**: live refresh → data-health validation (2 tests) →
  category + parameter questions → confirmation → `data-validator` → `design-output`
  (chart/table/KPI, always) → `data-freshness` footer. Do not skip or reorder stages.
