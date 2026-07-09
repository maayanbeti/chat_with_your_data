from access_api.flight_sql import import_and_export_flights


def main() -> None:
    import_and_export_flights(
        json_path="data/sample_flights.json",
        db_path="data/flights.sqlite3",
        csv_path="data/flights.csv",
    )


if __name__ == "__main__":
    main()
