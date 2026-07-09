---
name: clarification-flight
description: |
  Use this skill EVERY TIME a user asks a question about flight data. Before answering any flight-related query, present an interactive clarification form to collect essential filter parameters.
  
  Trigger phrases: "how many flights", "which flights", "flight statistics", "flight data", "flights with", "count of flights", "tell me about flights", or ANY question about flight information.
  
  The skill presents a three-part interactive form asking about: (1) landing date range, (2) departure date range, (3) flight status filters. User selections determine which flights to analyze in the response.
compatibility: |
  - Access to flight data (CSV file with columns: landing date, departure date, flight status)
  - HTML/JavaScript for interactive form rendering
---

# ✈️ Flight Data Clarification Skill

## Purpose

Before answering ANY question about flight data, collect essential filter parameters from the user through an interactive form. This ensures accurate, focused analysis by confirming exactly which flights the user wants to analyze.

## When to Use This Skill

**Use this skill for EVERY flight data question**, including:
- "How many flights do we have?"
- "Show me flight statistics"
- "Which flights arrived on time?"
- "How many flights departed yesterday?"
- "How many flights to Larnaca?"
- Any other flight-related analysis or counting query

**CRITICAL: The skill runs BEFORE answering. NO answer is provided until the form is submitted.**

---

## How It Works

### Step 1: Display Introduction Message

When the user asks ANY flight data question, start with:

> "Thank you for asking, we would like to clarify a few things before answering."

Then immediately display the interactive form (see below). **STOP - do not answer the question yet.**

### Step 2: Present Interactive Clarification Form

Display an interactive HTML form with three sections:

#### **Section 1: Landing Date Range** 📅
**Question:** "On what dates would you like to look for landing dates?"

**User options:**
- Radio button: "All dates" (no filtering)
- Radio button: "Custom range" (reveals date picker fields below)

**Date picker fields** (appear only when "Custom range" is selected):
- Start date field (type="date")
- End date field (type="date")

#### **Section 2: Departure Date Range** 📅
**Question:** "On what dates would you like to look for departure dates?"

**User options:**
- Radio button: "All dates" (no filtering)
- Radio button: "Custom range" (reveals date picker fields below)

**Date picker fields** (appear only when "Custom range" is selected):
- Start date field (type="date")
- End date field (type="date")

#### **Section 3: Flight Status** ✈️
**Question:** "Which flight statuses would you like to include?"

**Multi-select checkboxes** (user can select multiple):
- ☑ 🛬 landed
- ☑ 🛫 departed
- ☑ ❌ canceled
- ☑ ✅ on time
- ☑ ⏳ not final
- ☑ ⏰ delayed
- ☑ 📍 landing
- ☑ 🎯 final
- ☑ ⚡ early

**Default behavior:** If no status is selected, ALL statuses are included by default.

**Helper buttons:**
- "✓ Select all" — checks all status boxes at once
- "✗ Clear all" — unchecks all status boxes

### Step 3: Submit and Process

**OK Button:**
- Button text: "OK ✓"
- Action: User clicks to confirm selections
- Display confirmation message showing all selected filters
- Status message confirms: "✓ Selections received"

Once clicked, extract the user's selections:
1. Landing date range (all or custom start/end dates)
2. Departure date range (all or custom start/end dates)
3. Selected flight statuses (or all if none selected)

### Step 4: WAIT for Form Submission

**BLOCKING STEP:** Do NOT answer the question until the user submits the form and you see the confirmation message with their selections.

### Step 5: Answer the Question Based on Form Selections

ONLY AFTER the user clicks OK and selections are confirmed, answer the user's original flight question using ONLY the flights that match these filters:

```
Filtered flights = All flights WHERE
  (landing_date BETWEEN landing_start AND landing_end OR landing_range = "all")
  AND (departure_date BETWEEN departure_start AND departure_end OR departure_range = "all")
  AND (flight_status IN selected_statuses OR no_statuses_selected)
```

Include the filter summary in your response for clarity:
> "Based on your selections (landing dates: [range], departure dates: [range], statuses: [list]), you have [COUNT] flights."

---

## Visual Design & UX

### Styling & Emojis
- Use clear, friendly language
- Include relevant emojis throughout the form (📅 for dates, ✈️ for status, ☑ for checkboxes)
- Highlight selected items visually (checkmarks, highlighted buttons)
- Make date pickers easy to use with calendar interface

### Form Layout
- Display all three sections on one form
- Use clear section headers with emojis
- Group related elements (radio buttons together, checkboxes grouped)
- Keep spacing clean and readable
- OK button should be prominent at the bottom

### Interactive Behavior
- Date picker fields only appear when "Custom range" is selected (progressive disclosure)
- Visual feedback when user clicks/selects items
- All three sections visible and clearable at any time
- Select all / Clear all buttons for convenience

---

## Example Flow

```
👤 User: "How many flights do we have?"

🤖 Claude: "Thank you for asking, we would like to clarify a few things before answering."
         [Interactive form appears with all three questions]
         [WAITING - no answer yet]

👤 User selects:
   - Landing dates: All dates
   - Departure dates: All dates
   - Flight statuses: [no selections]

👤 User clicks OK

🤖 Confirmation: "Selections received: Landing all dates | Departure all dates | Status all statuses"

📊 Claude responds:
   "Based on your selections (all landing dates, all departure dates, all statuses), 
    you have 2,434 flights in total."
```

---

## Key Behavior: Blocking Form

**The form is ALWAYS shown first. The answer ONLY comes after form submission.**

- User asks any flight question → Form appears immediately
- NO answer is given while form is open
- User submits form → Confirmation shown → Answer provided
- If user asks another flight question → Form appears again (for new filters)

---

## Implementation Notes

**CRITICAL RULE:** This skill MUST run and be COMPLETED before answering ANY flight question.

- **Blocking behavior**: Display form, then WAIT. No answer text until form is submitted.
- **Every flight question triggers form**: "how many flights", "flights to X", "flight count", etc. — ALL require form first.
- Date inputs should support calendar picker (HTML5 date input)
- Multi-select checkboxes work by allowing multiple ☑ marks
- If user closes form without submitting, ask them to complete it
- This is an interactive, blocking form — answer doesn't come until user submits
- Always show what filters were applied in your final answer for transparency
- Show confirmation message when form is submitted (e.g., "Selections received: Landing all dates, Departure all dates, Status all statuses")
- Then provide the answer based on those selections
