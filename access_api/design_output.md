# Skill: design_output

Convert structured question payloads into chart and output specifications for data visualization.

## Overview

This skill provides utilities to:
1. Accept a question payload with intent, dataset context, and result schema
2. Apply rule-based chart selection logic
3. Generate visualization specifications with formatting, transform rules, and confidence scores
4. Support multilingual datasets with language-aware column selection
5. Standardize display output as JPEG for rendered chart/image artifacts
6. Standardize KPI presentation as an indicator with a closed percentage diff versus a prior period

## Functions

### `design_output(question_payload: Dict[str, Any]) -> Dict[str, Any]`

Design an output specification from a question payload.

**Parameters:**
- `question_payload` (Dict[str, Any]): A structured question payload containing:
  - `question` (str): Natural language question, e.g., "What's the distribution of airlines by percentage?"
  - `intent` (str): Query intent, e.g., "distribution", "trend", "comparison", "summary"
  - `dataset_context` (Dict): Context about the data:
    - `domain` (str): Data domain, e.g., "flights"
    - `grain` (str): Row-level description
    - `columns` (Dict[str, str]): Column name to description mapping
  - `result_schema` (List[Dict]): Expected result columns with types (dimension/metric)
  - `row_count` (int): Number of rows in result

**Returns:**
- `Dict[str, Any]` containing:
  - `output_type` (str): Type of visualization ("pie_chart", "bar_chart", "table", etc.)
  - `confidence` (float): Confidence score (0.0 to 1.0) for this recommendation
  - `title` (str): Chart title derived from the question
  - `chart` (Dict): Chart configuration with kind, fields, and fallback options
  - `transform` (Dict, optional): Data transform rules (grouping, sorting, limits)
  - `formatting` (Dict, optional): Visual formatting options
  - `explanation` (str): Reasoning for the chosen output type

**Rendering conventions:**
- Display rendered output files in JPEG format.
- For KPI rate questions (for example, cancellation rate, on-time rate, delay rate), display an indicator with a closed percentage diff.
- Example KPI phrasing: "Cancellation rate this week was 20% (+10%)." This indicates an increase versus the previous period.

**Example:**
```python
from access_api.design_output import design_output

payload = {
    "question": "What's the distribution of airlines by percentage?",
    "intent": "distribution",
    "dataset_context": {
        "domain": "flights",
        "grain": "one row per flight",
        "columns": {
            "airline_name": "airline name",
            "airline_code": "airline code",
            "flight_status": "status"
        }
    },
    "result_schema": [
        {"name": "airline", "type": "dimension"},
        {"name": "flight_count", "type": "metric"},
        {"name": "percentage", "type": "metric"}
    ],
    "row_count": 56
}

spec = design_output(payload)
# Returns:
# {
#     "output_type": "pie_chart",
#     "confidence": 0.86,
#     "title": "What's the distribution of airlines by percentage",
#     "chart": {
#         "kind": "pie",
#         "label_field": "airline_name",
#         "value_field": "percentage",
#         "fallback": {
#             "kind": "bar_chart",
#             "reason": "Use bar chart if there are more than 8 visible categories"
#         }
#     },
#     "transform": {
#         "limit": 8,
#         "group_remaining_as": "Other",
#         "sort": "percentage_desc"
#     },
#     "formatting": {
#         "percentage_decimals": 1,
#         "show_legend": true,
#         "show_labels": true
#     },
#     "explanation": "A pie chart works because the question asks for part-to-whole percentage distribution."
# }
```

### `_title_from_question(question: str) -> str`

Extract and clean a chart title from a question string.

**Parameters:**
- `question` (str): The natural language question

**Returns:**
- Cleaned title with trailing "?" removed

**Example:**
```python
_title_from_question("What's the distribution of airlines?")
# Returns: "What's the distribution of airlines"
```

### `_pick_label_field(columns: Dict[str, str]) -> str`

Intelligently select a label field from available columns.

**Parameters:**
- `columns` (Dict[str, str]): Mapping of column names to descriptions

**Returns:**
- The most suitable column name for labels, or "label" as fallback

**Priority order:**
1. `airline_name`
2. `airline`
3. `category`
4. `name`
5. `destination_country`
6. `destination_city`
7. `label` (fallback)

**Example:**
```python
columns = {
    "airline_name": "airline name",
    "flight_count": "count",
    "percentage": "percentage"
}

field = _pick_label_field(columns)
# Returns: "airline_name"
```

## Intent Types

The skill currently supports the following intents:

### `distribution`

- **Use case**: Part-to-whole analysis (e.g., market share, percentages, proportions)
- **Output**: Pie chart (with bar chart fallback for >8 categories)
- **Transform**: Groups by category, limits to top 8, remaining as "Other"
- **Confidence**: 0.86

### Default (Fallback)

- **Use case**: Any unrecognized intent
- **Output**: Table
- **Confidence**: 0.5
- **Explanation**: Tables are safe for any data result

## Integration

The skill is used in the "ask data" workflow to convert structured question payloads into actionable visualization designs:

```python
from access_api.design_output import design_output
from access_api.flight_sql import run_query

# Execute a query
rows = run_query("SELECT airline_name, COUNT(*) as count FROM flights GROUP BY airline_name")

# Design output from question payload
payload = {
    "question": "What airlines are in this dataset?",
    "intent": "distribution",
    "dataset_context": { ... },
    "result_schema": [ ... ],
    "row_count": len(rows)
}

spec = design_output(payload)
# Use spec to render chart in frontend or export to visualization tool
```

## Use Cases

- **Auto-generated Dashboards**: Convert natural language questions into charts
- **Result Visualization**: Recommend output format based on query intent
- **Data Exploration**: Quickly preview results with appropriate visualizations
- **Multilingual Datasets**: Select appropriate display columns (e.g., `airline_name_en` vs `airline_name_heb`)
- **Report Generation**: Create consistent chart specs for automated reporting

## Future Extensions

Potential enhancements:
- Support for "trend" intent (line charts over time)
- Support for "comparison" intent (grouped bar charts)
- Support for "ranking" intent (horizontal bar charts)
- Support for "summary" intent (KPI cards)
- Dynamic category limit based on chart dimensions
- Column type inference from result_schema
- Language preference propagation from dataset_context
