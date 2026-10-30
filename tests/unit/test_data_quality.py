import pytest

from fund_quality.data_quality import (
    map_fund_id,
    validate_fund_id,
    validate_numeric_rules,
    validate_required_fields,
    validate_valuation_date,
)


@pytest.fixture
def valid_record():
    return {
        "source_fund_id": "EXT-F001",
        "valuation_date": "2024-02-29",
        "units_held": 1000,
        "nav": 12.50,
        "expected_aum": 12500.00,
    }


def test_map_valid_fund_id():
    assert map_fund_id("EXT-F001") == "F001"


def test_map_unknown_fund_id():
    with pytest.raises(ValueError, match="Unknown fund ID"):
        map_fund_id("EXT-F999")


def test_map_fund_id_requires_prefix():
    with pytest.raises(ValueError, match="must start with EXT-"):
        map_fund_id("F001")


def test_map_fund_id_rejects_empty_value():
    with pytest.raises(ValueError, match="missing"):
        map_fund_id("")


def test_required_fields_pass_for_valid_record(valid_record):
    assert validate_required_fields(valid_record) == []


def test_required_fields_detect_missing_nav(valid_record):
    valid_record["nav"] = None

    assert validate_required_fields(valid_record) == ["nav is missing"]


def test_valid_leap_day():
    assert validate_valuation_date("2024-02-29") is True


@pytest.mark.parametrize(
    "invalid_date",
    ["2023-02-29", "2024-13-01", "not-a-date", "2024-2-09", None],
)
def test_invalid_valuation_dates(invalid_date):
    assert validate_valuation_date(invalid_date) is False


def test_numeric_rules_pass_for_valid_record(valid_record):
    assert validate_numeric_rules(valid_record) == []


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("units_held", -1, "units_held cannot be negative"),
        ("nav", -1, "nav cannot be negative"),
        ("nav", 0, "nav must be greater than zero"),
        ("units_held", 1.5, "units_held must be a whole number"),
        ("nav", "invalid", "nav must be numeric"),
        ("expected_aum", -10, "expected_aum cannot be negative"),
    ],
)
def test_numeric_rule_violations(valid_record, field, value, expected_error):
    valid_record[field] = value

    assert expected_error in validate_numeric_rules(valid_record)


def test_fund_id_validation_passes(valid_record):
    assert validate_fund_id(valid_record) == []


def test_fund_id_validation_detects_unknown_id(valid_record):
    valid_record["source_fund_id"] = "EXT-F999"

    assert "Unknown fund ID: F999" in validate_fund_id(valid_record)