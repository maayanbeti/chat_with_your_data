---
name: data-validator-skill-new
description: |
  ALWAYS validate flight count answers BEFORE presenting them to users. This skill QA checks that the calculated flight count is accurate based on applied filters from the clarification form.
  
  Trigger AFTER answer is calculated but BEFORE presenting to user. Recounts flights from CSV file using the same filters and compares results. Returns VALID ✓ (answer is correct) or INVALID ✗ (answer is wrong - block and ask user to resubmit).
  
  Use this skill for EVERY flight question to ensure accuracy and data integrity.

compatibility: |
  - Access to flight data CSV file (datafile.csv)
  - Filter parameters: landing_date_range, departure_date_range, flight_status, destination
  - Calculated count from previous answer
---

# ✈️ Data Validator Skill - New Version

## Purpose

Validate that flight count answers are accurate BEFORE presenting them to users. If validation fails, BLOCK the answer and ask the user to resubmit with corrected parameters.

## When to Use This Skill

**ALWAYS use this skill BEFORE showing any flight count answer**, including:
- "You have 2,434 flights" (total count)
- "Found 47 flights to Larnaka" (destination filtered)
- "12 flights to Japan with custom dates" (multi-filter)
- Any flight query with calculated count

**CRITICAL:** This skill runs AFTER answer calculation but BEFORE user sees the result.

---

## How It Works

### Input Parameters

The validator receives:
- **Landing Date Range:** "all" or custom range (start_date, end_date)
- **Departure Date Range:** "all" or custom range (start_date, end_date)
- **Flight Statuses:** List of selected statuses (or empty for all)
- **Destination:** Country/Airport name (if destination-filtered query)
- **Calculated Count:** The flight count to validate

### Validation Steps

#### Step 1: Validate Filter Parameters ✅

**Check each filter:**
- Landing date: If custom, is start_date <= end_date? (valid format?)
- Departure date: If custom, is start_date <= end_date? (valid format?)
- Status list: Are all values in valid set? (landed, departed, canceled, on time, not final, delayed, landing, final, early)
- Destination: Is destination name valid/recognized?

**Result:** 
- ✅ PASS - All parameters are valid
- ❌ FAIL - Invalid parameter detected (return which one)

#### Step 2: Recount Flights from CSV ✅

**Open datafile.csv and apply filters:**

```
Filtered flights = CSV WHERE
  (landing_date BETWEEN start_date AND end_date OR range="all")
  AND (departure_date BETWEEN start_date AND end_date OR range="all")
  AND (flight_status IN selected_statuses OR statuses_empty)
  AND (destination MATCHES destination_name OR destination_unspecified)
```

**Count matching rows:** Total = number of rows that match all filters

#### Step 3: Compare Counts ✅

**Compare:**
- Recounted flights = X
- Provided count = Y
- Match? X == Y

**Result:**
- ✅ PASS - Counts match exactly
- ❌ FAIL - Counts differ (show: expected X, got Y)

#### Step 4: Validate Specific Cases ✅

**Check edge cases:**
- Empty result: Is count 0? Is that correct for filters?
- Single result: Is count 1? Verify it matches filters
- Large count: Does it make sense for filters?

**Result:**
- ✅ PASS - Edge case handled correctly
- ⚠️ WARNING - Unusual result (flag for review)

---

## Validation Result Format

### VALID ✓ Response

```
VALIDATION: ✓ VALID

Status: Answer is accurate
Filters Applied:
- Landing dates: [range]
- Departure dates: [range]
- Statuses: [list or all]
- Destination: [name or all]

Count Verified: [number] flights
Evidence: Recounted [number] flights from CSV - count matches ✓
```

**Action:** Present answer to user

### INVALID ✗ Response

```
VALIDATION: ✗ INVALID

Status: Answer is INCORRECT - BLOCKED
Reason: [specific issue]

Details:
- Expected count: [X] flights
- Provided count: [Y] flights
- Difference: [X-Y] flights

Issue: [explanation of what went wrong]
```

**Action:** Block answer and show this message to user:

> ❌ **Answer validation failed.** The calculated flight count doesn't match our records. Please:
> 1. Review your filter selections
> 2. Click OK again with correct filters
> 3. We'll verify the new count before showing results

---

## Validation Rules

**CRITICAL RULES:**
- ✅ Validator MUST run before answer presentation
- ✅ Validator MUST have access to flight CSV file
- ✅ Validator MUST recount flights independently
- ✅ Validator MUST compare counts exactly
- 🚫 Validator MUST BLOCK invalid answers (don't show to user)
- ✅ Validator MUST ask user to resubmit if invalid

**Error Handling:**
- If CSV file not found → ⚠️ Return WARNING (can't validate but show answer with caveat)
- If filter logic error → ❌ Return INVALID (block answer)
- If count mismatch → ❌ Return INVALID (block answer)

**Data Integrity:**
- Use exact match for destination (case-insensitive but name match)
- Use date comparison for range validation
- Use set comparison for status selection
- Count rows that match ALL conditions (AND logic)

---

## Status Codes

| Status | Icon | Meaning | Action |
|--------|------|---------|--------|
| VALID | ✓ | Count is correct | Show answer to user |
| INVALID | ✗ | Count is wrong | Block answer, ask resubmit |
| WARNING | ⚠️ | Can't fully validate | Show answer with disclaimer |

---

## Workflow Integration

**Sequence:**
1. User asks flight question
2. Form captures filters (clarification-flight skill)
3. Answer is calculated
4. **→ VALIDATOR RUNS** ← (this skill)
5. If VALID ✓ → Answer presented
6. If INVALID ✗ → Error message shown, form redisplayed
7. User resubmits with corrected filters
8. Back to step 3 (recalculate + revalidate)
