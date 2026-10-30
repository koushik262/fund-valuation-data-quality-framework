from decimal import Decimal

import pytest

from fund_quality.validation import (
    calculate_aum,
    validate_aum,
    validate_record,
)


def test_calculate_aum():
    assert calculate_aum(1000, 12.50) == Decimal("12500.00")


def test_calculate_aum_rounds_half_up():
    assert calculate_aum(3, 1.235) == Decimal("3.71")


def test_calculate_aum_rejects_negative_units():
    with pytest.raises(ValueError, match="Units held cannot be negative"):
        calculate_aum(-100, 10)


def test_calculate_aum_rejects_negative_nav():
    with pytest.raises(ValueError, match="NAV cannot be negative"):
        calculate_aum(100, -10)


def test_calculate_aum_rejects_invalid_input():
    with pytest.raises(ValueError, match="valid numbers"):
        calculate_aum("invalid", 10)


def test_validate_aum_passes_for_correct_value():
    assert validate_aum(1000, 12.50, 12500.00) is True


def test_validate_aum_allows_configured_tolerance():
    assert validate_aum(1000, 12.50, 12500.01, tolerance="0.01") is True


def test_validate_aum_fails_outside_tolerance():
    assert validate_aum(1000, 12.50, 12500.05, tolerance="0.01") is False


def test_validate_aum_rejects_negative_tolerance():
    with pytest.raises(ValueError, match="Tolerance cannot be negative"):
        validate_aum(1000, 12.50, 12500, tolerance="-0.01")


def test_validate_record_passes_for_valid_record():
    record = {
        "units_held": 1000,
        "nav": 12.50,
        "expected_aum": 12500.00,
    }

    assert validate_record(record) == []


def test_validate_record_detects_incorrect_aum():
    record = {
        "units_held": 1000,
        "nav": 12.50,
        "expected_aum": 12000.00,
    }

    assert "AUM does not match units_held * nav" in validate_record(record)


def test_validate_record_detects_missing_nav():
    record = {
        "units_held": 1000,
        "nav": None,
        "expected_aum": 12500.00,
    }

    assert "nav is missing" in validate_record(record)