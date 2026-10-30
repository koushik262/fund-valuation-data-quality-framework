import pandas as pd


def remove_mart_record(data: pd.DataFrame) -> pd.DataFrame:
    """Simulate a record lost during Mart processing."""
    if data.empty:
        return data.copy()

    return data.iloc[:-1].copy().reset_index(drop=True)


def corrupt_final_aum(data: pd.DataFrame) -> pd.DataFrame:
    """Simulate an incorrect AUM value in the Final layer."""
    result = data.copy()

    if not result.empty:
        result.loc[result.index[0], "expected_aum"] = (
            float(result.loc[result.index[0], "expected_aum"]) + 100
        )

    return result


def inject_missing_nav(data: pd.DataFrame) -> pd.DataFrame:
    """Simulate a missing NAV value in the source data."""
    result = data.copy()

    if not result.empty:
        result.loc[result.index[0], "nav"] = None
        result.loc[result.index[0], "expected_aum"] = None

    return result