import pandas as pd
import pytest

from fund_quality.synthetic_data import (
    VALUATION_DATES,
    add_correction,
    add_exact_duplicate,
    add_invalid_units,
    add_null_nav,
    create_synthetic_data,
)


def test_generator_returns_expected_number_of_records():
    data = create_synthetic_data()

    assert len(data) == 12
    assert data["source_fund_id"].nunique() == 3
    assert data["valuation_date"].nunique() == 4


def test_generator_is_deterministic():
    first_run = create_synthetic_data()
    second_run = create_synthetic_data()

    pd.testing.assert_frame_equal(first_run, second_run)


def test_clean_data_has_no_null_values():
    data = create_synthetic_data()

    assert not data.isnull().any().any()


def test_clean_data_has_positive_units_and_nav():
    data = create_synthetic_data()

    assert (data["units_held"] > 0).all()
    assert (data["nav"] > 0).all()


def test_expected_aum_matches_units_times_nav():
    data = create_synthetic_data()

    calculated_aum = (data["units_held"] * data["nav"]).round(2)

    assert calculated_aum.equals(data["expected_aum"])


def test_leap_day_is_included():
    data = create_synthetic_data()

    assert "2024-02-29" in data["valuation_date"].values


def test_weekend_gap_is_represented():
    data = create_synthetic_data()
    dates = sorted(data["valuation_date"].unique())

    assert dates == VALUATION_DATES
    assert "2024-03-02" not in dates
    assert "2024-03-03" not in dates


def test_exact_duplicate_injection_adds_one_record():
    clean_data = create_synthetic_data()
    defective_data = add_exact_duplicate(clean_data)

    assert len(defective_data) == len(clean_data) + 1
    assert defective_data.duplicated().sum() == 1


def test_correction_injection_preserves_both_versions():
    clean_data = create_synthetic_data()
    defective_data = add_correction(clean_data)

    first_fund = clean_data.iloc[0]["source_fund_id"]
    first_date = clean_data.iloc[0]["valuation_date"]

    matching = defective_data[
        (defective_data["source_fund_id"] == first_fund)
        & (defective_data["valuation_date"] == first_date)
    ]

    assert len(matching) == 2
    assert set(matching["record_version"]) == {1, 2}
    assert matching["nav"].nunique() == 2


def test_null_nav_injection_creates_missing_value():
    defective_data = add_null_nav(create_synthetic_data())

    assert defective_data["nav"].isnull().sum() == 1


def test_invalid_units_injection_creates_negative_value():
    defective_data = add_invalid_units(create_synthetic_data())

    assert (defective_data["units_held"] < 0).any()