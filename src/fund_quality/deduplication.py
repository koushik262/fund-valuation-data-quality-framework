import pandas as pd


BUSINESS_KEY = ["source_fund_id", "valuation_date"]


def remove_exact_duplicates(data: pd.DataFrame) -> pd.DataFrame:
    """Remove rows identical across all columns."""
    return data.drop_duplicates().reset_index(drop=True)


def keep_latest_correction(data: pd.DataFrame) -> pd.DataFrame:
    """
    Keep the latest version of each fund/date valuation.

    Higher record_version wins. If versions tie, the later updated_at
    timestamp wins.
    """
    required = BUSINESS_KEY + ["record_version", "updated_at"]
    missing = [column for column in required if column not in data.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    result = data.copy()

    result["record_version"] = pd.to_numeric(
        result["record_version"], errors="raise"
    )
    result["updated_at"] = pd.to_datetime(
        result["updated_at"], errors="raise"
    )

    result = result.sort_values(
        BUSINESS_KEY + ["record_version", "updated_at"],
        kind="stable",
    )

    result = result.drop_duplicates(
        subset=BUSINESS_KEY,
        keep="last",
    )

    return result.reset_index(drop=True)