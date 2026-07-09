# chat_with_your_data
AI agent for chatting with your data — connects to data.gov.il datastore APIs (and other sources) to let users query and explore datasets in natural language. Built as part of an AI analytics bootcamp.

## Ask Data workflow
Use the automatic import-and-rename pipeline for flight data:

```bash
python3 -m access_api.flight_sql --json data/sample_flights.json --db data/flights.sqlite3 --csv data/flights.csv
```

This step imports the source JSON into SQLite and exports a renamed CSV with analytics-friendly column names.
