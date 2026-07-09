# Skill: flight_rename_rows

Convert API data to renamed CSV with language annotations and analytics metadata.

## Overview

This skill provides utilities to:
1. Export SQL query results to CSV files
2. Rename columns according to a flexible mapping
3. Automatically classify columns by language (_heb for Hebrew, _en for English)
4. Generate analytics metadata for downstream processing

## Functions

### `detect_language(column_name: str) -> Optional[str]`

Detects language from column name suffix.

**Parameters:**
- `column_name` (str): The column name to inspect

**Returns:**
- `'hebrew'` if suffix is `_heb` or `_he`
- `'english'` if suffix is `_en`
- `None` otherwise

**Example:**
```python
detect_language('destination_city_heb')  # Returns: 'hebrew'
detect_language('flight_status_en')      # Returns: 'english'
detect_language('airline_code')          # Returns: None
```

### `export_to_csv_with_rename(rows, column_mapping, output_path) -> Path`

Export rows to CSV with renamed columns and language detection.

**Parameters:**
- `rows` (List[Dict[str, Any]]): List of dictionaries with row data
- `column_mapping` (Dict[str, str]): Mapping of old column names to new names
- `output_path` (Union[Path, str]): Where to save the CSV file

**Returns:**
- `Path` to the saved CSV file

**Example:**
```python
from access_api.flight_rename_rows import export_to_csv_with_rename

mapping = {
    '_id': 'id',
    'CHOPER': 'airline_code',
    'CHRMINE': 'flight_status_en',
    'CHRMINH': 'flight_status_heb'
}

rows = [
    {'_id': 1, 'CHOPER': 'LY', 'CHRMINE': 'LANDED', 'CHRMINH': 'נחתה'},
    {'_id': 2, 'CHOPER': 'AF', 'CHRMINE': 'SCHEDULED', 'CHRMINH': 'מתוכנן'},
]

path = export_to_csv_with_rename(rows, mapping, 'output.csv')
```

### `get_column_metadata(column_mapping) -> Dict[str, Dict[str, str]]`

Generate analytics metadata for renamed columns.

**Parameters:**
- `column_mapping` (Dict[str, str]): Mapping of old column names to new names

**Returns:**
- Dictionary with column metadata including:
  - `original_name`: The original column name from the API
  - `language`: Detected language ('hebrew', 'english', or None)
  - `is_translatable`: Boolean flag indicating if column has language variant

**Example:**
```python
from access_api.flight_rename_rows import get_column_metadata

mapping = {
    'CHRMINE': 'flight_status_en',
    'CHRMINH': 'flight_status_heb'
}

metadata = get_column_metadata(mapping)
# Returns:
# {
#   'flight_status_en': {
#     'original_name': 'CHRMINE',
#     'language': 'english',
#     'is_translatable': True
#   },
#   'flight_status_heb': {
#     'original_name': 'CHRMINH',
#     'language': 'hebrew',
#     'is_translatable': True
#   }
# }
```

## Default Mappings

### `FLIGHT_COLUMNS`

Pre-configured column mapping for Ben Gurion Airport flight data:

| Original | Renamed | Language |
|----------|---------|----------|
| `_id` | `id` | - |
| `CHOPER` | `airline_code` | - |
| `CHFLTN` | `flight_num` | - |
| `CHOPERD` | `airline_name` | - |
| `CHSTOL` | `scheduled_dt` | - |
| `CHPTOL` | `actual_dt` | - |
| `CHAORD` | `departure_ind` | - |
| `CHLOC1` | `destination_airport_code` | - |
| `CHLOC1D` | `destination_airport_name` | - |
| `CHLOC1TH` | `destination_city_heb` | hebrew |
| `CHLOC1T` | `destination_city_en` | english |
| `CHLOC1CH` | `destination_country_heb` | hebrew |
| `CHLOCCT` | `destination_country_en` | english |
| `CHTERM` | `terminal_num` | - |
| `CHCINT` | `checkin_counter` | - |
| `CHCKZN` | `checkin_zone` | - |
| `CHRMINE` | `flight_status_en` | english |
| `CHRMINH` | `flight_status_heb` | hebrew |

## Integration

The skill is integrated into `access_api/flight_sql.py` via the `export_flights_to_csv()` function:

```python
from access_api.flight_sql import export_flights_to_csv

# Export all flights to CSV with renamed columns
path = export_flights_to_csv()

# Returns: /data/flights.csv with metadata output
```

## Use Cases

- **Data Standardization**: Rename API fields to analytics-friendly names
- **Multilingual Support**: Identify and tag columns by language for translation workflows
- **Data Export**: Convert SQL queries to CSV for spreadsheet tools
- **Metadata Generation**: Automatically classify columns for data catalogs

## New skill: design_output

You can also generate an output design spec from a natural-language question payload using [access_api/design_output.py](access_api/design_output.py).

### Example
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
            "departure_ind": "arrival or departure",
            "destination_country": "country",
            "destination_city": "city",
            "scheduled_dt": "scheduled time",
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
print(spec)
```
