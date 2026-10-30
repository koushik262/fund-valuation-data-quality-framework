import pandas as pd
import pytest

from fund_quality.deduplication import (
    keep_latest_correction,
    remove_exact_duplicates,
)


@pytest.fixture
def valuation_data():
    return pd.DataFrame(
        [
            {
                "source_fund_id": "EXT-F001",
                "valuation_date": "2024-02-29",
                "units_held": 1000,
                "nav": 12.50,
                "expected_aum": 12500.00,
                "record_version": 1,
                "updated_at": "2024-02-29T18:00:00",
            },
            {
                "source_fund_id": "EXT-F001",
                "valuation_date": "2024-02-29",
                "units_held": 1000,
                "nav": 12.50,
                "expected_aum": 12500.00,
                "record_version": 1,
                "updated_at": "2024-02-29T18:00:00",
            },
            {
                "source_fund_id": "EXT-F001",
                "valuation_date": "2024-02-29",
                "units_held": 1000,
                "nav": 13.75,
                "expected_aum": 13750.00,
                "record_version": 2,
                "updated_at": "2024-02-29T20:00:00",
            },
            {
                "source_fund_id": "EXT-F002",
                "valuation_date": "2024-02-29",
                "units_held": 2000,
                "nav": 10.00,
                "expected_aum": 20000.00,
                "record_version": 1,
                "updated_at": "2024-02-29T18:00:00",
            },
        ]
    )


def test_remove_exact_duplicates(valuation_data):
    result = remove_exact_duplicates(valuation_data)

    assert len(result) == 3
    assert result.duplicated().sum() == 0


def test_keep_latest_correction(valuation_data):
    result = keep_latest_correction(valuation_data)

    assert len(result) == 2

    corrected = result[
        (result["source_fund_id"] == "EXT-F001")
        & (result["valuation_date"] == "2024-02-29")
    ]

    assert len(corrected) == 1
    assert corrected.iloc[0]["record_version"] == 2
    assert corrected.iloc[0]["nav"] == 13.75


def test_latest_correction_keeps_other_funds(valuation_data):
    result = keep_latest_correction(valuation_data)

    assert "EXT-F002" in result["source_fund_id"].values


def test_missing_required_columns_raise_error():
    data = pd.DataFrame(
        [{"source_fund_id": "EXT-F001", "valuation_date": "2024-02-29"}]
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        keep_latest_correction(data)


def test_empty_dataframe_is_supported():
    data = pd.DataFrame(
        columns=[
            "source_fund_id",
            "valuation_date",
            "record_version",
            "updated_at",
        ]
    )

    result = keep_latest_correction(data)

    assert result.empty