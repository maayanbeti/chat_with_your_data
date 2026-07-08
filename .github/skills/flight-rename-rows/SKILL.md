---
name: flight-rename-rows
description: "Convert API flight rows to renamed CSV output with language-aware column tags and export metadata. Use for renaming query results, classifying Hebrew/English columns, and generating a flight CSV export."
user-invocable: true
---

# Flight Rename Rows

Use this skill when you need to export flight API or SQL rows into a CSV with standardized column names and language-aware metadata.

## What It Does
- Renames API columns using the flight mapping in `access_api/flight_rename_rows.py`
- Detects language from column suffixes such as `_heb`, `_he`, and `_en`
- Builds column metadata for downstream analytics or cataloging
- Exports renamed rows to UTF-8 CSV

## When to Use
- You have flight query results and want analytics-friendly column names
- You need to preserve Hebrew and English variants in separate fields
- You want a reusable Ben Gurion flight export mapping

## Procedure
1. Import the helpers from `access_api/flight_rename_rows.py`.
2. Use `FLIGHT_COLUMNS` or provide a custom mapping.
3. Call `export_to_csv_with_rename(rows, column_mapping, output_path)`.
4. Use `get_column_metadata(column_mapping)` if you need a catalog or schema summary.

## References
- [Python implementation](../../../access_api/flight_rename_rows.py)
- [Skill notes](../../../access_api/flight_rename_rows.md)
