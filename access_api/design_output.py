from typing import Any, Dict


def design_output(question_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Design a visualization spec from a question payload.

    Rule name: visualization_output.
    """
    question = question_payload.get("question", "")
    intent = question_payload.get("intent", "").lower()
    dataset_context = question_payload.get("dataset_context", {})
    columns = dataset_context.get("columns", {})
    row_count = int(question_payload.get("row_count") or 0)
    question_lc = question.lower()
    title = _title_from_question(question)
    signals = _extract_signals(question_lc, intent, row_count)
    selected_output_type = _select_output_type(signals)

    # 1) Table for listing, exact values, or detail-heavy asks.
    if selected_output_type == "table":
        return {
            "output_type": "table",
            "confidence": 0.9,
            "title": title,
            "chart": {"kind": "table"},
            "explanation": "A table is best for top/list/detail requests and exact-value comparison.",
        }

    # 2) Bar chart for category comparisons.
    if selected_output_type == "bar_chart":
        return {
            "output_type": "bar_chart",
            "confidence": 0.88,
            "title": title,
            "chart": {
                "kind": "bar",
                "label_field": _pick_label_field(columns),
                "value_field": _pick_value_field(question_payload),
            },
            "transform": {
                "sort": "value_desc",
            },
            "explanation": "A bar chart is best for comparing values across categories.",
        }

    # 3) Donut for part-to-whole share.
    if selected_output_type == "donut_chart":
        return {
            "output_type": "donut_chart",
            "confidence": 0.86,
            "title": title,
            "chart": {
                "kind": "donut",
                "label_field": _pick_label_field(columns),
                "value_field": _pick_value_field(question_payload),
                "fallback": {
                    "kind": "bar_chart",
                    "reason": "Use bar chart when visible categories exceed 8.",
                },
            },
            "transform": {
                "limit": 8,
                "group_remaining_as": "Other",
                "sort": "value_desc",
            },
            "formatting": {
                "percentage_decimals": 1,
                "value_decimals": 0,
                "show_legend": True,
                "show_labels": True,
                "show_values": True,
                "show_percentages": True,
                "label_template": "{name}: {value} ({percent})",
            },
            "explanation": "A donut chart matches part-to-whole share questions.",
        }

    # 4) Line chart for time-oriented asks.
    if selected_output_type == "line_chart":
        return {
            "output_type": "line_chart",
            "confidence": 0.9,
            "title": title,
            "chart": {
                "kind": "line",
                "x_field": _pick_time_field(columns),
                "y_field": _pick_value_field(question_payload),
                "series_field": _pick_series_field(columns),
                "y_axis": {
                    "min": 0,
                    "start_at_zero": True,
                },
            },
            "explanation": "A line chart is best for trend and over-time questions.",
        }

    # 5) KPI cards for single-number asks.
    if selected_output_type == "kpi_cards":
        kpi_polarity = _kpi_metric_polarity(question_lc)
        is_rate = _is_rate_question(question_lc)
        spec = {
            "output_type": "kpi_cards",
            "confidence": 0.9,
            "title": title,
            "chart": {
                "kind": "kpi_cards",
                "value_field": _pick_value_field(question_payload),
                "comparison": {
                    "enabled": True,
                    "baseline": "previous_period",
                    "display": "parenthetical",
                    "show_arrow": True,
                    "metric_polarity": kpi_polarity,
                    "direction_rule": {
                        "negative_metric": {
                            "increase": {
                                "arrow": "up",
                                "color": "red",
                            },
                            "decrease": {
                                "arrow": "down",
                                "color": "green",
                            },
                        },
                        "positive_metric": {
                            "increase": {
                                "arrow": "up",
                                "color": "green",
                            },
                            "decrease": {
                                "arrow": "down",
                                "color": "red",
                            },
                        },
                    },
                },
            },
            "explanation": "KPI cards are ideal for single-number answers.",
        }
        if is_rate:
            spec["chart"]["indicator"] = {
                "enabled": True,
                "format": "percentage",
                "decimals": 1,
                "show_arrow": True,
                "show_color": True,
                "polarity": kpi_polarity,
            }
            spec["explanation"] = "Rate questions display a KPI indicator with a directional arrow and polarity color."
        return spec

    # 6) Stacked bar for category split by another category.
    if selected_output_type == "stacked_bar_chart":
        return {
            "output_type": "stacked_bar_chart",
            "confidence": 0.89,
            "title": title,
            "chart": {
                "kind": "stacked_bar",
                "label_field": _pick_label_field(columns),
                "stack_field": _pick_stack_field(columns),
                "value_field": _pick_value_field(question_payload),
            },
            "explanation": "A stacked bar chart compares totals and composition across categories.",
        }

    return {
        "output_type": "table",
        "confidence": 0.5,
        "title": title,
        "chart": {"kind": "table"},
        "explanation": "No strong chart pattern matched; a table is the safest fallback.",
    }


def _extract_signals(question_lc: str, intent: str, row_count: int) -> Dict[str, Any]:
    """Extract boolean decision signals used by the output type selector."""
    return {
        "is_table_query": _is_table_query(question_lc),
        "is_category_comparison": _is_category_comparison(question_lc),
        "is_time_series": _is_time_series(question_lc),
        "is_part_to_whole": _is_part_to_whole(question_lc),
        "is_single_number": _is_single_number(question_lc),
        "is_category_split": _is_category_split(question_lc),
        "intent": intent,
        "row_count": row_count,
    }


def _select_output_type(signals: Dict[str, Any]) -> str:
    """Select the output type with stable rule precedence."""
    if signals["is_table_query"]:
        return "table"

    if signals["is_category_comparison"]:
        return "bar_chart"

    if (signals["intent"] == "distribution" and not signals["is_time_series"]) or signals["is_part_to_whole"]:
        return "donut_chart"

    if signals["is_time_series"]:
        return "line_chart"

    if signals["is_single_number"]:
        return "kpi_cards"

    if signals["is_category_split"]:
        return "stacked_bar_chart"

    return "fallback_table"


def _title_from_question(question: str) -> str:
    if not question:
        return "Question Output"
    return question.rstrip("?")


def _pick_label_field(columns: Dict[str, str]) -> str:
    for candidate in ["airline_name", "airline", "category", "name", "destination_country", "destination_city"]:
        if candidate in columns:
            return candidate
    return "label"


def _pick_time_field(columns: Dict[str, str]) -> str:
    for candidate in ["scheduled_dt", "actual_dt", "time", "hour", "date", "day"]:
        if candidate in columns:
            return candidate
    return "time"


def _pick_series_field(columns: Dict[str, str]) -> str:
    for candidate in ["airline_name", "airline", "terminal", "departure_ind", "flight_status"]:
        if candidate in columns:
            return candidate
    return "series"


def _pick_stack_field(columns: Dict[str, str]) -> str:
    for candidate in ["departure_ind", "flight_status", "terminal", "status", "category"]:
        if candidate in columns:
            return candidate
    return "segment"


def _pick_value_field(question_payload: Dict[str, Any]) -> str:
    for field in question_payload.get("result_schema", []):
        if field.get("type") == "metric":
            return field.get("name", "value")
    return "value"


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _is_table_query(question_lc: str) -> bool:
    return _contains_any(
        question_lc,
        [
            "top ",
            "list",
            "show me",
            "compare exact values",
            "details",
            "rows",
            "flights by airline",
        ],
    )


def _is_category_comparison(question_lc: str) -> bool:
    return _contains_any(
        question_lc,
        [
            "which airlines have the most flights",
            "which airline has the most delays",
            "which destinations had the most cancellations",
            "which terminal is the busiest",
            "flights by country",
            "top destinations",
            "most flights",
            "most delays",
            "most cancellations",
            "busiest",
            "on-time rate per airline",
            "compare the number of flights to",
            "per airline",
            "by country",
            "by destination",
        ],
    )


def _is_part_to_whole(question_lc: str) -> bool:
    if _contains_any(question_lc, ["share", "part-to-whole", "proportion"]):
        return True

    if "distribution" in question_lc and _contains_any(question_lc, ["percentage", "%", "share"]):
        return True

    return "departures vs arrivals" in question_lc


def _is_time_series(question_lc: str) -> bool:
    return _contains_any(
        question_lc,
        [
            "over time",
            "hourly",
            "per hour",
            "daily trend",
            "trend",
            "by hour",
            "by day",
            "timeline",
        ],
    )


def _is_single_number(question_lc: str) -> bool:
    if _contains_any(question_lc, [" by ", " per ", " vs ", "versus", "distribution", "trend", "over time"]):
        return False

    return _contains_any(
        question_lc,
        [
            "how many ",
            "what is the average",
            "average ",
            "total ",
            "what percentage",
            " rate",
            "how much",
        ],
    )


def _is_rate_question(question_lc: str) -> bool:
    """Return True when the question is asking for a rate metric (percentage indicator)."""
    return _contains_any(
        question_lc,
        [
            "cancellation rate",
            "cancel rate",
            "on-time rate",
            "ontime rate",
            "delay rate",
            "departure rate",
            "arrival rate",
            "punctuality rate",
            "what is the rate",
            "what rate",
            " rate",
        ],
    ) and not _contains_any(question_lc, [" by ", " per airline", " per terminal", " per destination"])


def _is_category_split(question_lc: str) -> bool:
    split_signal = _contains_any(
        question_lc,
        [
            "arrival vs departure",
            "arrivals and departures",
            "status distribution",
            "departures vs arrivals",
            " vs ",
            "versus",
        ],
    )
    has_group_dimension = _contains_any(question_lc, [" by ", " per "])

    return split_signal and has_group_dimension


def _kpi_metric_polarity(question_lc: str) -> str:
    if _contains_any(question_lc, ["cancel", "cancellation", "delay", "delayed", "error", "failure"]):
        return "negative_metric"
    return "positive_metric"
