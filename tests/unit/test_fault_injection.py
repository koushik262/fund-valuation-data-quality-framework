from fund_quality.fault_injection import (
    corrupt_final_aum,
    inject_missing_nav,
    remove_mart_record,
)
from fund_quality.synthetic_data import create_synthetic_data


def test_remove_mart_record_reduces_count():
    source = create_synthetic_data()

    mart = remove_mart_record(source)

    assert len(mart) == len(source) - 1


def test_corrupt_final_aum_changes_value():
    source = create_synthetic_data()

    final = corrupt_final_aum(source)

    assert (
        final.loc[0, "expected_aum"]
        != source.loc[0, "expected_aum"]
    )


def test_inject_missing_nav_creates_null():
    source = create_synthetic_data()

    defective = inject_missing_nav(source)

    assert defective["nav"].isnull().sum() == 1