"""Client for the data.gov.il CKAN datastore API.

API docs: https://data.gov.il/api/3/action/help_show?name=datastore_search
"""

import json

import requests

BASE_URL = "https://data.gov.il/api/3/action"


def search_datasets(query, rows=10):
    """Search for datasets (packages) matching a free-text query."""
    response = requests.get(
        f"{BASE_URL}/package_search", params={"q": query, "rows": rows}
    )
    response.raise_for_status()
    return response.json()["result"]


def get_records(resource_id, query=None, filters=None, limit=100, offset=0):
    """Fetch records from a datastore resource, optionally filtered by a
    free-text query and/or exact-match field filters.
    """
    params = {"resource_id": resource_id, "limit": limit, "offset": offset}
    if query:
        params["q"] = query
    if filters:
        params["filters"] = json.dumps(filters)

    response = requests.get(f"{BASE_URL}/datastore_search", params=params)
    response.raise_for_status()
    return response.json()["result"]


def sql_query(sql):
    """Run a read-only SQL query against the datastore.

    Example: sql_query('SELECT * FROM "resource-id-here" LIMIT 5')
    """
    response = requests.get(f"{BASE_URL}/datastore_search_sql", params={"sql": sql})
    response.raise_for_status()
    return response.json()["result"]
