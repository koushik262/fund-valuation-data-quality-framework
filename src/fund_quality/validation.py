from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


def calculate_aum(
    units_held: Any,
    nav: Any,
) -> Decimal:
    """Calculate AUM as units held multiplied by NAV, rounded to 2 decimals."""
    try:
        units = Decimal(str(units_held))
        nav_value = Decimal(str(nav))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Units held and NAV must be valid numbers") from exc

    if not units.is_finite() or not nav_value.is_finite():
        raise ValueError("Units held and NAV must be finite numbers")

    if units < 0:
        raise ValueError("Units held cannot be negative")

    if nav_value < 0:
        raise ValueError("NAV cannot be negative")

    aum = units * nav_value
    return aum.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_aum(
    units_held: Any,
    nav: Any,
    reported_aum: Any,
    tolerance: Any = "0.01",
) -> bool:
    """Check whether reported AUM matches the calculated AUM within tolerance."""
    try:
        reported = Decimal(str(reported_aum))
        allowed_difference = Decimal(str(tolerance))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("Reported AUM and tolerance must be valid numbers") from exc

    if not reported.is_finite() or not allowed_difference.is_finite():
        raise ValueError("Reported AUM and tolerance must be finite numbers")

    if allowed_difference < 0:
        raise ValueError("Tolerance cannot be negative")

    calculated = calculate_aum(units_held, nav)
    return abs(calculated - reported) <= allowed_difference


def validate_record(record: dict) -> list[str]:
    """Return validation errors for a single valuation record."""
    errors = []

    units = record.get("units_held")
    nav = record.get("nav")
    reported_aum = record.get("expected_aum")

    if units is None:
        errors.append("units_held is missing")
    if nav is None:
        errors.append("nav is missing")
    if reported_aum is None:
        errors.append("expected_aum is missing")

    if errors:
        return errors

    try:
        if not validate_aum(units, nav, reported_aum):
            errors.append("AUM does not match units_held * nav")
    except ValueError as exc:
        errors.append(str(exc))

    return errors