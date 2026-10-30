import pandas as pd
import pytest

from fund_quality.reconciliation import (
    find_missing_funds,
    reconcile_tables,
    summarize_table,
)


@pytest.fixture
def source_data():
    return pd.DataFrame(
        [
            {"source_fund_id": "EXT-F001", "expected_aum": 1000.00},
            {"source_fund_id": "EXT-F002", "expected_aum": 2000.00},
            {"source_fund_id": "EXT-F001", "expected_aum": 1100.00},
        ]
    )


def test_summarize_table(source_data):
    summary = summarize_table(source_data, "source")

    assert summary["record_count"] == 3
    assert summary["distinct_funds"] == 2
    assert summary["total_aum"] == 4100.00


def test_all_layers_reconcile_when_identical(source_data):
    result = reconcile_tables(
        source_data,
        source_data.copy(),
        source_data.copy(),
        source_data.copy(),
    )

    assert result["reconciliation_passed"].all()


def test_reconciliation_detects_missing_record(source_data):
    landing = source_data.iloc[:-1].copy()

    result = reconcile_tables(
        source_data,
        landing,
        source_data,
        source_data,
    )

    landing_result = result[result["table"] == "landing"].iloc[0]

    assert landing_result["counts_match"] is False or not landing_result["counts_match"]
    assert not landing_result["reconciliation_passed"]


def test_reconciliation_detects_aum_difference(source_data):
    mart = source_data.copy()
    mart.loc[0, "expected_aum"] = 900.00

    result = reconcile_tables(
        source_data,
        source_data.copy(),
        mart,
        source_data.copy(),
    )

    mart_result = result[result["table"] == "mart"].iloc[0]

    assert not mart_result["aum_matches"]
    assert not mart_result["reconciliation_passed"]


def test_missing_funds_are_detected(source_data):
    final = source_data[
        source_data["source_fund_id"] != "EXT-F002"
    ].copy()

    missing = find_missing_funds(source_data, final)

    assert missing == {"EXT-F002"}


def test_empty_target_reports_all_funds_missing(source_data):
    empty_target = source_data.iloc[0:0].copy()

    assert find_missing_funds(source_data, empty_target) == {
        "EXT-F001",
        "EXT-F002",
    }


def test_invalid_tolerance_is_rejected(source_data):
    with pytest.raises(ValueError, match="Tolerance"):
        reconcile_tables(
            source_data,
            source_data,
            source_data,
            source_data,
            tolerance="-1",
        )


def test_null_aum_is_rejected(source_data):
    invalid_data = source_data.copy()
    invalid_data.loc[0, "expected_aum"] = None

    with pytest.raises(ValueError, match="null AUM"):
        summarize_table(invalid_data, "source")