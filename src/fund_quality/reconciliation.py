from decimal import Decimal, InvalidOperation

import pandas as pd


REQUIRED_COLUMNS = {"source_fund_id", "expected_aum"}


def _validate_table(data: pd.DataFrame, table_name: str) -> None:
    missing = REQUIRED_COLUMNS - set(data.columns)

    if missing:
        raise ValueError(
            f"{table_name} is missing required columns: {sorted(missing)}"
        )


def _to_decimal(value, table_name: str) -> Decimal:
    if pd.isna(value):
        raise ValueError(f"{table_name} contains a null AUM value")

    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(
            f"{table_name} contains a non-numeric AUM value"
        ) from exc

    if not result.is_finite():
        raise ValueError(f"{table_name} contains a non-finite AUM value")

    return result


def summarize_table(
    data: pd.DataFrame,
    table_name: str,
) -> dict:
    """Summarize record count, distinct funds, and total AUM."""
    _validate_table(data, table_name)

    aum_values = [
        _to_decimal(value, table_name)
        for value in data["expected_aum"]
    ]

    return {
        "table": table_name,
        "record_count": len(data),
        "distinct_funds": data["source_fund_id"].nunique(),
        "total_aum": sum(aum_values, Decimal("0.00")),
    }


def reconcile_tables(
    source: pd.DataFrame,
    landing: pd.DataFrame,
    mart: pd.DataFrame,
    final: pd.DataFrame,
    tolerance: str = "0.01",
) -> pd.DataFrame:
    """
    Compare counts and total AUM at each pipeline layer against source.

    Assumes each layer represents the same batch and business scope.
    """
    allowed_difference = Decimal(str(tolerance))

    if not allowed_difference.is_finite() or allowed_difference < 0:
        raise ValueError("Tolerance must be a finite, non-negative number")

    tables = [
        ("source", source),
        ("landing", landing),
        ("mart", mart),
        ("final", final),
    ]

    summaries = [
        summarize_table(data, name)
        for name, data in tables
    ]

    source_summary = summaries[0]
    rows = []

    for summary in summaries:
        count_diff = summary["record_count"] - source_summary["record_count"]
        aum_diff = summary["total_aum"] - source_summary["total_aum"]

        rows.append(
            {
                "table": summary["table"],
                "record_count": summary["record_count"],
                "source_record_count": source_summary["record_count"],
                "record_count_difference": count_diff,
                "distinct_funds": summary["distinct_funds"],
                "total_aum": float(summary["total_aum"]),
                "source_total_aum": float(source_summary["total_aum"]),
                "aum_difference": float(aum_diff),
                "counts_match": count_diff == 0,
                "aum_matches": abs(aum_diff) <= allowed_difference,
                "reconciliation_passed": (
                    count_diff == 0
                    and abs(aum_diff) <= allowed_difference
                ),
            }
        )

    return pd.DataFrame(rows)


def find_missing_funds(
    source: pd.DataFrame,
    target: pd.DataFrame,
) -> set[str]:
    """Return fund IDs present in source but absent from a target layer."""
    _validate_table(source, "source")
    _validate_table(target, "target")

    source_funds = set(source["source_fund_id"].dropna().unique())
    target_funds = set(target["source_fund_id"].dropna().unique())

    return source_funds - target_funds