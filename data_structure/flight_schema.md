# Dataset: Ben Gurion Airport Flight Board (CHAMA)

Source: data.gov.il datastore, resource id `e83f763b-b7d7-479e-b172-ae981ddc6de5`
Fetched via `access_api.get_records`. Total rows: 2,438.

## Columns

| Column     | Type    | Description                                              |
|------------|---------|------------------------------------------------------------|
| `_id`      | int     | Row identifier                                             |
| `CHOPER`   | text    | Airline IATA code (e.g. `LY`)                              |
| `CHFLTN`   | text    | Flight number                                               |
| `CHOPERD`  | text    | Airline name                                                |
| `CHSTOL`   | text    | Scheduled time of landing/departure (ISO 8601)              |
| `CHPTOL`   | text    | Predicted/actual time of landing/departure (ISO 8601)        |
| `CHAORD`   | text    | Arrival/Departure indicator (`A` = arrival, `D` = departure) |
| `CHLOC1`   | text    | Origin/destination airport IATA code (e.g. `LCA`)            |
| `CHLOC1D`  | text    | Origin/destination airport name (English)                    |
| `CHLOC1TH` | text    | Origin/destination city name (Hebrew)                        |
| `CHLOC1T`  | text    | Origin/destination city name (English)                       |
| `CHLOC1CH` | text    | Origin/destination country name (Hebrew)                     |
| `CHLOCCT`  | text    | Origin/destination country name (English)                    |
| `CHTERM`   | numeric | Terminal number                                              |
| `CHCINT`   | text    | Check-in counter(s)                                          |
| `CHCKZN`   | text    | Check-in zone                                                |
| `CHRMINE`  | text    | Flight status (English, e.g. `LANDED`)                       |
| `CHRMINH`  | text    | Flight status (Hebrew, e.g. `נחתה`)                          |

## Sample record

```json
{
  "_id": 1,
  "CHOPER": "LY",
  "CHFLTN": "5142",
  "CHOPERD": "EL AL ISRAEL AIRLINES",
  "CHSTOL": "2026-06-30T16:25:00",
  "CHPTOL": "2026-06-30T18:47:00",
  "CHAORD": "A",
  "CHLOC1": "LCA",
  "CHLOC1D": "LARNACA",
  "CHLOC1TH": "לרנקה",
  "CHLOC1T": "LARNACA",
  "CHLOC1CH": "קפריסין",
  "CHLOCCT": "CYPRUS",
  "CHTERM": 3,
  "CHCINT": null,
  "CHCKZN": null,
  "CHRMINE": "LANDED",
  "CHRMINH": "נחתה"
}
```
