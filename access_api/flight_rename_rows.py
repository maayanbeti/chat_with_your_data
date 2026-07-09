"""
Skill: Convert API data to renamed CSV with language annotations.

This skill provides utilities to:
1. Export SQL query results to CSV
2. Rename columns according to a mapping
3. Classify columns by language (_heb for Hebrew, _en for English)
4. Tag columns for analytics purposes
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def detect_language(column_name: str) -> Optional[str]:
    """Detect language from column suffix.
    
    Args:
        column_name: The column name to inspect
        
    Returns:
        'hebrew' if suffix is _heb or _he, 'english' if suffix is _en, else None
    """
    if column_name.endswith('_heb') or column_name.endswith('_he'):
        return 'hebrew'
    elif column_name.endswith('_en'):
        return 'english'
    return None


def export_to_csv_with_rename(
    rows: List[Dict[str, Any]],
    column_mapping: Dict[str, str],
    output_path: Union[Path, str],
) -> Path:
    """Export rows to CSV with renamed columns and language detection.
    
    Args:
        rows: List of dictionaries with row data
        column_mapping: Mapping of old column names to new names
        output_path: Where to save the CSV file
        
    Returns:
        Path to the saved CSV file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not rows:
        raise ValueError("No rows to export")
    
    old_cols = list(rows[0].keys())
    new_cols = [column_mapping.get(col, col) for col in old_cols]
    
    with output_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(new_cols)
        for row in rows:
            writer.writerow([row[col] for col in old_cols])
    
    return output_path


def get_column_metadata(column_mapping: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """Generate analytics metadata for renamed columns.
    
    Args:
        column_mapping: Mapping of old column names to new names
        
    Returns:
        Dictionary with column metadata including language tags
    """
    metadata = {}
    for old_name, new_name in column_mapping.items():
        lang = detect_language(new_name)
        metadata[new_name] = {
            'original_name': old_name,
            'language': lang,
            'is_translatable': lang is not None,
        }
    return metadata


# Default column mapping for Ben Gurion Airport flight data
FLIGHT_COLUMNS = {
    '_id': 'id',
    'CHOPER': 'airline_code',
    'CHFLTN': 'flight_num',
    'CHOPERD': 'airline_name',
    'CHSTOL': 'scheduled_dt',
    'CHPTOL': 'actual_dt',
    'CHAORD': 'departure_ind',
    'CHLOC1': 'destination_airport_code',
    'CHLOC1D': 'destination_airport_name',
    'CHLOC1TH': 'destination_city_heb',
    'CHLOC1T': 'destination_city_en',
    'CHLOC1CH': 'destination_country_heb',
    'CHLOCCT': 'destination_country_en',
    'CHTERM': 'terminal_num',
    'CHCINT': 'checkin_counter',
    'CHCKZN': 'checkin_zone',
    'CHRMINE': 'flight_status_en',
    'CHRMINH': 'flight_status_heb'
}
