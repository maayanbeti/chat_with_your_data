# Dataset: תקציב עיריית באר-שבע (Be'er Sheva Municipal Budget)

Source: data.gov.il datastore, resource id `2d66eb8f-a3cd-45c8-8cfe-39f48d833e72`
Fetched via `access_api.get_records`. Total rows: 87,742.

## Columns

| Column     | Type    | Description                        |
|------------|---------|-------------------------------------|
| `_id`      | int     | Row identifier                     |
| `שנה`      | numeric | Budget year                        |
| `חשבון`    | numeric | Account number                     |
| `שם חשבון` | text    | Account name                       |
| `מחלקה`    | text    | Department                          |
| `מקורי`    | text    | Original budget amount             |
| `מעודכן`   | text    | Updated/revised budget amount       |
| `ביצוע`    | numeric | Actual execution amount            |

## Sample record

```json
{
  "_id": 1,
  "שנה": 2009,
  "חשבון": 1111000110,
  "שם חשבון": "ארנונה - גביה שוטפת",
  "מחלקה": null,
  "מקורי": null,
  "מעודכן": null,
  "ביצוע": -413528842
}
```
