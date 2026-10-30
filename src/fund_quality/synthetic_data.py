from pathlib import Path
import random

import pandas as pd


SEED = 42

VALUATION_DATES = [
    "2024-02-27",
    "2024-02-28",
    "2024-02-29",  # Leap day
    "2024-03-04",  # Weekend gap after March 1
]

FUND_IDS = ["F001", "F002", "F003"]


def create_synthetic_data(seed: int = SEED) -> pd.DataFrame:
    """Create deterministic, clean synthetic fund valuation records."""
    rng = random.Random(seed)
    records = []

    for date_index, valuation_date in enumerate(VALUATION_DATES):
        for fund_index, fund_id in enumerate(FUND_IDS):
            units_held = rng.randint(1_000, 10_000)

            # Generate a positive NAV with two decimal places.
            nav = round(
                rng.randint(500, 5_000) / 100,
                2,
            )

            expected_aum = round(units_held * nav, 2)

            records.append(
                {
                    "batch_id": f"BATCH-{valuation_date.replace('-', '')}",
                    "source_fund_id": f"EXT-{fund_id}",
                    "valuation_date": valuation_date,
                    "units_held": units_held,
                    "nav": nav,
                    "expected_aum": expected_aum,
                    "record_version": 1,
                    "updated_at": f"{valuation_date}T18:00:00",
                }
            )

    return pd.DataFrame(records)


def add_exact_duplicate(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with one exact duplicate record appended."""
    result = data.copy()
    duplicate = result.iloc[[0]].copy()

    return pd.concat([result, duplicate], ignore_index=True)


def add_correction(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with a newer version of an existing valuation."""
    result = data.copy()
    corrected = result.iloc[[0]].copy()

    corrected.loc[:, "record_version"] = 2
    corrected.loc[:, "nav"] = round(float(corrected.iloc[0]["nav"]) + 1.25, 2)
    corrected.loc[:, "expected_aum"] = round(
        float(corrected.iloc[0]["units_held"])
        * float(corrected.iloc[0]["nav"]),
        2,
    )
    corrected.loc[:, "updated_at"] = (
        f"{corrected.iloc[0]['valuation_date']}T20:00:00"
    )

    return pd.concat([result, corrected], ignore_index=True)


def add_null_nav(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with one missing NAV value."""
    result = data.copy()
    result.loc[0, "nav"] = None
    result.loc[0, "expected_aum"] = None

    return result


def add_invalid_units(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with one invalid negative units value."""
    result = data.copy()
    result.loc[0, "units_held"] = -100

    return result


def write_synthetic_data(output_path: str | Path) -> Path:
    """Generate the clean dataset and save it as CSV."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    data = create_synthetic_data()
    data.to_csv(output, index=False)

    return output


if __name__ == "__main__":
    output_file = write_synthetic_data(
        "data/synthetic/source_clean.csv"
    )
    print(f"Generated synthetic data: {output_file}")