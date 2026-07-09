---
name: data-validator
description: |
  Validates Claude's answers about flight data analysis BEFORE final results are presented. 
  
  Use this skill to check:
  - Did Claude ask clarifying questions when the user's request was ambiguous?
  - Did Claude use the correct data threshold (e.g., "5 minutes late" not 30 minutes)?
  - Did Claude filter correctly (e.g., only LANDED flights, not DEPARTED)?
  - Are calculations accurate (percentages, counts, time differences)?
  
  Trigger on EVERY flight data question: "Which company...", "How many flights...", "What's the best...", etc.
  Report: VALID ✅ | NEEDS CLARIFICATION ⚠️ | INCORRECT ❌

compatibility: |
  - Access to flights.csv file in project folder
  - Can read and analyze CSV data
---

## Overview

Before Claude provides final results to the user about flight data analysis, this skill validates that:
1. **Clarifying questions were asked** when needed
2. **Data thresholds are correct** (user's preference is being used)
3. **Data filters are correct** (right flight status, date range, etc.)
4. **Calculations are accurate** (counts, percentages, time differences)

This ensures the user gets accurate, well-reasoned answers.

---

## Validation Rules

### Rule 1: Clarifying Questions Required
**When to validate:**
- User asks about "on-time arrivals" → Claude MUST ask: "What's your on-time threshold?"
- User asks about "popular companies" → Claude MUST ask: "What metric? (flights, destinations, frequency)"
- User asks about "flight details" → Claude MUST ask: "Language preference? (Hebrew/English)"
- User asks about "flights to destination" → Claude MUST ask: "Landing or arrival?"

**Status:**
- ✅ VALID: Question was asked and user answered
- ⚠️ NEEDS CLARIFICATION: Question asked but no answer yet
- ❌ INCORRECT: Question not asked for ambiguous query

---

### Rule 2: Threshold Compliance
**When to validate:**
- User specifies "5 minutes late" → Check Claude uses ≤5 min, not other thresholds
- User specifies "±15 minutes" → Check Claude uses -15 to +15, not other range
- User specifies "0-30 minutes" → Check Claude uses exactly that range

**Status:**
- ✅ VALID: Threshold used matches user's specification exactly
- ⚠️ NEEDS CLARIFICATION: Threshold unclear or not specified yet
- ❌ INCORRECT: Wrong threshold used (e.g., used 30 when user said 5)

---

### Rule 3: Data Filtering
**When to validate:**
- "How many flights arrived?" → Must filter: Status = "LANDED" only
- "Yesterday's arrivals?" → Must filter: Date = 2026-07-04 (or user-specified date)
- "Which airlines?" → Must group correctly by airline code/name

**Status:**
- ✅ VALID: Correct filters applied (LANDED only, correct date range)
- ⚠️ NEEDS CLARIFICATION: Filtering described but not verified against data
- ❌ INCORRECT: Wrong filters (included DEPARTED, wrong date, etc.)

---

### Rule 4: Calculation Accuracy
**When to validate:**
- On-time count: Total flights within threshold ÷ Total arrived flights
- Percentage: (On-time count ÷ Total arrived) × 100
- Time difference: (Actual arrival - Scheduled arrival) in minutes
- Airline rankings: Sorted by on-time percentage (highest first)

**Status:**
- ✅ VALID: Calculations match expected formula
- ⚠️ NEEDS CLARIFICATION: Calculations described but not fully verified
- ❌ INCORRECT: Math is wrong (e.g., percentage > 100%, negative counts)

---

## Validation Workflow

**Before Claude presents final results:**

1. **Check Question Asked** → Was the clarifying question asked? (Rule 1)
2. **Check Threshold** → Does Claude's answer use the user's threshold? (Rule 2)
3. **Check Filters** → Are the right flights selected? (Rule 3)
4. **Check Math** → Are the calculations correct? (Rule 4)

**Report Status:**
```
✅ VALID
  All validation rules passed. Answer is ready to present.

⚠️ NEEDS CLARIFICATION
  Issue: [describe what's missing]
  Action: Ask user for clarification

❌ INCORRECT
  Issue: [describe the error]
  Action: Recalculate or re-analyze with correct parameters
```

---

## Example Validation

**User asks:** "How many flights arrived on time yesterday?"

**Claude should:**
1. Ask: "What's your on-time threshold?" → User: "5 minutes late"
2. Filter: LANDED flights on 2026-07-04
3. Calculate: Count flights where 0 ≤ time difference ≤ 5 minutes
4. Result: "95 LANDED flights, 42 on-time (44.2%)"

**Validator checks:**
- ✅ Asked clarifying question
- ✅ Uses 5-minute threshold (not 30, not 15)
- ✅ Filtered by LANDED and correct date
- ✅ Math: 42/95 = 44.2% ✓

**Status:** ✅ VALID

---

## Notes

- Validation happens AFTER Claude answers, before presenting to user
- If validation fails, Claude should recalculate or ask for clarification
- User can override validation if they believe Claude is correct
- Validation builds confidence in data-driven decisions
