import csv
import tempfile
import unittest
from pathlib import Path

from access_api.design_output import design_output
from access_api.flight_sql import export_flights_to_csv, import_and_export_flights, load_flights, run_query


class FlightSqlTests(unittest.TestCase):
    def test_load_flights_and_query(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        json_path = repo_root / "data" / "sample_flights.json"

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "flights.sqlite3"
            load_flights(json_path=json_path, db_path=db_path)

            rows = run_query(
                "SELECT CHOPERD, CHFLTN FROM flights WHERE CHAORD = 'D' ORDER BY _id",
                db_path=db_path,
            )

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["CHFLTN"], "123")
            self.assertEqual(rows[1]["CHFLTN"], "890")

    def test_import_and_export_flights_creates_renamed_csv(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        json_path = repo_root / "data" / "sample_flights.json"

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "flights.sqlite3"
            csv_path = Path(tmpdir) / "flights.csv"
            import_and_export_flights(json_path=json_path, db_path=db_path, csv_path=csv_path)

            with csv_path.open("r", encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))

            self.assertEqual(rows[0][0], "id")
            self.assertEqual(rows[0][1], "airline_code")
            self.assertEqual(rows[1][0], "1")
            self.assertEqual(rows[1][1], "LY")

    def test_design_output_creates_pie_chart_spec(self) -> None:
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

        self.assertEqual(spec["output_type"], "pie_chart")
        self.assertEqual(spec["chart"]["kind"], "pie")
        self.assertEqual(spec["chart"]["label_field"], "airline_name")
        self.assertEqual(spec["chart"]["value_field"], "percentage")
        self.assertEqual(spec["formatting"]["percentage_decimals"], 1)


if __name__ == "__main__":
    unittest.main()
