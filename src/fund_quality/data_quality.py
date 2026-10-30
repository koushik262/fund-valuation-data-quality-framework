from datetime import date
from decimal import Decimal, InvalidOperation


REQUIRED_FIELDS = [
    "source_fund_id",
    "valuation_date",
    "units_held",
    "nav",
    "expected_aum",
]

KNOWN_FUND_IDS = {"F001", "F002", "F003"}


def map_fund_id(source_fund_id: str) -> str:
    """Remove the external provider prefix from a fund ID."""
    if not isinstance(source_fund_id, str) or not source_fund_id.strip():
        raise ValueError("Source fund ID is missing")

    prefix = "EXT-"
    if not source_fund_id.startswith(prefix):
        raise ValueError("Source fund ID must start with EXT-")

    mapped_id = source_fund_id[len(prefix):]

    if mapped_id not in KNOWN_FUND_IDS:
        raise ValueError(f"Unknown fund ID: {mapped_id}")

    return mapped_id


def validate_required_fields(record: dict) -> list[str]:
    """Return errors for missing required fields."""
    errors = []

    for field in REQUIRED_FIELDS:
        value = record.get(field)

        if value is None or (
            isinstance(value, str) and not value.strip()
        ):
            errors.append(f"{field} is missing")

    return errors


def validate_valuation_date(value) -> bool:
    """Return True when value is a valid ISO date (YYYY-MM-DD)."""
    if not isinstance(value, str):
        return False

    try:
        parsed_date = date.fromisoformat(value)
    except ValueError:
        return False

    return parsed_date.isoformat() == value


def validate_numeric_rules(record: dict) -> list[str]:
    """Validate units, NAV, and expected AUM."""
    errors = []

    for field in ("units_held", "nav", "expected_aum"):
        value = record.get(field)

        if value is None or isinstance(value, bool):
            errors.append(f"{field} must be numeric")
            continue

        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            errors.append(f"{field} must be numeric")
            continue

        if not number.is_finite():
            errors.append(f"{field} must be finite")
            continue

        if field in ("units_held", "nav") and number < 0:
            errors.append(f"{field} cannot be negative")

        if field == "units_held" and number != number.to_integral_value():
            errors.append("units_held must be a whole number")

        if field == "nav" and number == 0:
            errors.append("nav must be greater than zero")

        if field == "expected_aum" and number < 0:
            errors.append("expected_aum cannot be negative")

    return errors


def validate_fund_id(record: dict) -> list[str]:
    """Validate and map a source fund ID."""
    try:
        map_fund_id(record.get("source_fund_id"))
    except ValueError as exc:
        return [str(exc)]

    return []