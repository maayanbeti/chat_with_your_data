from access_api.flight_sql import import_and_export_flights


def main() -> None:
    import_and_export_flights(
        db_path="data/flights.sqlite3",
        csv_path="data/flights.csv",
        source="live",
    )


if __name__ == "__main__":
    main()
