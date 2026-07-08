---
name: design-output
description: "Design chart and output specifications from structured question payloads for flight data analysis. Use for choosing a visualization type, title, label field, and fallback output."
user-invocable: true
---

# Design Output

Use this skill when you need to turn a structured question payload into a visualization or output specification.

## What It Does
- Chooses an output type from the payload intent
- Builds chart configuration and fallback behavior
- Derives a title from the natural-language question
- Picks a label field from available dataset columns
- Applies named visualization rules for common analytics question patterns
- Displays generated output files in JPEG format
- Uses donut charts for part-to-whole output and shows both values and percentages
- Forces line charts to start at zero on the Y axis
- Adds KPI comparison metadata (parenthetical delta, arrows, color semantics)
- For rate questions (cancellation rate, on-time rate, delay rate), always renders a KPI indicator with a closed percentage diff.
	Example: cancellation rate this week was 20% (+10%), which means it increased compared to the previous period.

## When to Use
- A query result needs a recommended chart or table layout
- You want a rule-based spec for distribution-style questions
- You need a fallback table for unrecognized intents
- You want consistent output behavior for table, bar, donut, line, KPI, and stacked bar cases

## Rules

Apply the named rule set in [visualization_output](./rules/visualization_output.md).

## Procedure
1. Build a question payload with `question`, `intent`, `dataset_context`, `result_schema`, and `row_count`.
2. Apply rules from [visualization_output](./rules/visualization_output.md).
3. Call `design_output(question_payload)` from `access_api/design_output.py`.
4. Render the returned `output_type`, `chart`, `transform`, and `formatting` values.
	Display the rendered output file as JPEG.
5. Use the `explanation` field to explain the recommendation to the user.

## References
- [Python implementation](../../../access_api/design_output.py)
- [Skill notes](../../../access_api/design_output.md)
- [Rules folder](./rules/visualization_output.md)
