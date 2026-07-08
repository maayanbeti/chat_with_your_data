---
name: clarify-questions
description: |
  Use this skill when a user asks questions about flight data that need clarification before analysis. This skill identifies ambiguous queries and asks focused clarifying questions to understand the user's intent, then helps execute the analysis on the flights.csv data.
  
  Trigger when users ask about:
  - Which companies/airlines arrived on time
  - Most popular/heavily used companies (by flights, destinations, or frequency)
  - Flight details and requirements (language preference)
  - Destinations with flights (landing vs. arrival distinction)
  
  Regardless of which of the above triggers, ALWAYS present the four selection-based filters (arrival time frame, departure time frame, flight status, output language) before generating a final response — see "Always-Ask Questions" below.
  
  After gathering clarifications, help the user query and analyze the flight data based on their specific needs.
compatibility: |
  - Access to flights.csv data file
  - Ability to read and analyze CSV data
  - Python or similar data processing capability
---

## Overview

When users ask questions about flight data, their queries often contain implicit assumptions or ambiguities that need clarification before you can provide accurate answers. This skill guides you through identifying which clarifications are needed and asking the right follow-up questions.

Once clarified, you'll help the user query and analyze the flights.csv dataset based on their specific requirements.

## Always-Ask Questions (Selection-Based, Mandatory for Every Query)

Before generating a final response to ANY flight data question — in addition to whichever rule-specific question applies below — always present these four filters as **selectable options** (dropdowns, radio buttons, or multi-selects). Users should not be required to type values manually.

### 0. Select All Data (Shortcut, Optional)
- Offer a single "Select all data (no filters)" option alongside the filters below. Choosing it sets Arrival Time Frame, Departure Time Frame, and Flight Status all to "No filter" in one action, so the user doesn't have to set each of the three individually.
- This shortcut does not cover Output Language — that selection is always required regardless of whether "Select all data" is chosen.

### 1. Arrival Time Frame (Optional)
- No arrival time filter
- Today
- Tomorrow
- Next 7 days
- Custom date range

### 2. Departure Time Frame (Optional)
- No departure time filter
- Today
- Tomorrow
- Next 7 days
- Custom date range

### 3. Flight Status (Optional)
- No status filter
- Scheduled
- Delayed
- Canceled
- Landed
- Diverted
- In Air

### 4. Output Language (Required)
- English only (`_en` columns)
- Hebrew only (`_heb` columns)
- Both English and Hebrew

**Rules:**
- Present the "Select all data" shortcut plus all four filters as selectable UI elements in a single clarifying turn — never as open free-text questions.
- Arrival Time Frame, Departure Time Frame, and Flight Status are each optional: default to "No filter" / "Any" if the user doesn't pick one (or if they choose "Select all data"), and proceed without narrowing on that dimension.
- Output Language is required in every case, with no "all"/default shortcut — the user must explicitly choose English only or Hebrew only (or Both) before results are presented, even if "Select all data" was chosen for the other filters.
- "Custom date range" (for either time frame) prompts for start/end dates via date pickers, not free-text.
- Wait for the user's selections before querying flights.csv.
- Apply the selections as filters/formatting on every subsequent query in the conversation until the user changes them.
- If the user has already made these selections earlier in the conversation, don't re-prompt — reuse the existing selections.

---

## Clarification Rules

### Rule 1: On-Time Arrival Questions
**When triggered by:** "Which companies arrived on time?", "What airlines were on-time?", "How many flights arrived on time?", etc.

**Ask the user:**
- "What's the maximum gap between actual arrival time and scheduled arrival time that you'd consider 'on-time'?" 
- Provide examples: "For example, 0-15 minutes early/late = on-time, or 0-30 minutes, etc."

**Example:**
- User: "How many flights arrived on time yesterday?"
- You: "What's the maximum gap between actual arrival time and scheduled arrival time that you'd consider as 'on-time'? For example, 0-15 minutes early/late, or 0-30 minutes?"
- User: "0-15 minutes early/late = on-time"
- You: Query flights.csv for LANDED flights within ±15 minutes and report the count

**After answer:** Query the flights.csv data to identify flights/companies meeting their on-time criteria and display results.

---

### Rule 2: Popular/Populated Company Questions
**When triggered by:** "Which company is most popular?", "What's the busiest airline?", "Which airline has the most flights?", etc.

**Ask the user:**
- "What metric would you like to measure popularity by?"
- Provide options:
  - Number of flights
  - Number of different destinations (arrival)

**After answer:** Query the flights.csv data and present the metric they chose, ranked by the selected measure.

---

### Rule 3: Flight Details Questions
**When triggered by:** "Show me flight details", "What information do you have about this flight?", "Tell me about airline X", etc.

**Ask the user:**
- Covered by the mandatory "Output Language" selection above — no need to ask again. Use that selection to decide Hebrew+English vs. English-only field display.

**After answer:** Provide flight details with these fields:
- **If Hebrew:** Display field names in both Hebrew and English
  - Airline Code | קוד חברה
  - Airline Name | שם חברה
  - Scheduled Arrival Time | שעת הגעה מתוכננת
  - Origin City | עיר מוצא
  - Origin Country | מדינת מוצא

- **If English only:** Display field names in English only
  - Airline Code
  - Airline Name
  - Scheduled Arrival Time
  - Origin City
  - Origin Country

---

### Rule 4: Destination Flight Questions
**When triggered by:** "Where do flights go?", "What flights go to X?", "Do we have flights to...?", etc.

**Ask the user:**
- "When you ask about flights to a destination, do you mean where the plane lands (final destination) or where passengers arrive?"
- Clarify if they're asking about landing airports vs. arrival terminals/cities.

**After answer:** Query the flights.csv for destinations matching their definition and display the results.

---

## Implementation Workflow

1. **Identify the question type** — Match the user's query against the 4 rules above
2. **Present the mandatory selection-based filters** — Arrival time frame, departure time frame, flight status (all optional), and output language (required) as dropdowns/radio buttons/multi-selects (see "Always-Ask Questions"), plus any rule-specific question that also applies, in one combined turn
3. **Wait for the user's selection(s)**
4. **Query the data** — Based on their selections, read flights.csv, filter by the chosen arrival/departure time frame(s) and flight status (skip any filter left as "No filter"/"Any"), and apply any rule-specific filters/analysis
5. **Present results** — Format output clearly, using Hebrew+English (`_heb`/`_en` columns), Hebrew-only (`_heb` columns), or English-only (`_en` columns) as specified

## Output Format

Structure results clearly:
- For on-time arrivals: List companies that meet the on-time threshold with flight counts
- For popular companies: Show ranking by chosen metric (flights, destinations, frequency)
- For flight details: Display as a table or structured list with appropriate language
- For destinations: List destinations with associated flight counts or details

---

## Notes

- Always present the four selection-based filters before assuming what the user means — never require free-text input for them
- The four filters (arrival time frame, departure time frame, flight status, output language) are mandatory for every flight data question, even if none of the 4 rule-specific triggers apply
- Arrival time frame, departure time frame, and flight status default to "No filter"/"Any" if left unselected; output language has no default and must be explicitly selected
- Be conversational, but stick to the clarification rules
- Once you have the selection(s), execute the query promptly
- If the user's question doesn't fit these 4 rule-specific categories, still present the mandatory selection-based filters, then proceed without a rule-specific question or adapt the closest rule to their intent
