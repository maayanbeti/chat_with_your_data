# chat_with_your_data
AI agent for chatting with your data — connects to data.gov.il datastore APIs (and other sources) to let users query and explore datasets in natural language. Built as part of an AI analytics bootcamp.

## Ask Data workflow
By default, the pipeline always pulls the **live** Ben Gurion flight board from
data.gov.il (resource `flydata`, which the source itself refreshes every 15 minutes) —
not a static local file:

```bash
python3 -m access_api.flight_sql
```

This fetches the current flight board, loads it into SQLite, and exports a renamed
CSV with analytics-friendly column names. Every flight question asked through the
`clarification-flight` skill / `master-workflow` agent triggers this same live
refresh first, so answers are never based on a stale snapshot.

For offline development/testing (no network), use the small local sample instead:

```bash
python3 -m access_api.flight_sql --source json --json data/sample_flights.json --db data/flights.sqlite3 --csv data/flights.csv
```
