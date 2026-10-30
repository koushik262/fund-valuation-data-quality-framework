import pandas as pd
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fund_quality.synthetic_data import create_synthetic_data
from fund_quality.validation import validate_record
from fund_quality.reconciliation import reconcile_tables
from fund_quality.reporting import generate_reports
from fund_quality.fault_injection import (
    corrupt_final_aum,
    inject_missing_nav,
    remove_mart_record,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenario",
        choices=["clean", "missing-mart-record", "incorrect-final-aum", "missing-nav"],
        default="clean",
        help="Choose a clean run or a simulated data-quality failure.",
    )
    args = parser.parse_args()

    print(f"Running scenario: {args.scenario}")

    source = create_synthetic_data()
    landing = source.copy()
    mart = landing.copy()
    final = mart.copy()

    if args.scenario == "missing-mart-record":
        mart = remove_mart_record(mart)
        final = mart.copy()
    elif args.scenario == "incorrect-final-aum":
        final = corrupt_final_aum(final)
    elif args.scenario == "missing-nav":
        source = inject_missing_nav(source)

    validation_errors = []

    for index, record in source.iterrows():
        errors = validate_record(record.to_dict())
        for error in errors:
            validation_errors.append(
                {
                    "record_id": f"ROW-{index + 1}",
                    "check": "record_validation",
                    "error": error,
                }
            )

    try:
        reconciliation = reconcile_tables(
            source=source,
            landing=landing,
            mart=mart,
            final=final,
        )
    except ValueError as exc:
        print(f"Reconciliation error: {exc}")

        source_count = len(source)
        table_data_list = [
            ("source", source),
            ("landing", landing),
            ("mart", mart),
            ("final", final),
        ]

        reconciliation = pd.DataFrame([
            {
                "table": table_name,
                "record_count": len(table_data),
                "source_record_count": source_count,
                "record_count_difference": len(table_data) - source_count,
                "distinct_funds": table_data["source_fund_id"].nunique(),
                "total_aum": None,
                "source_total_aum": None,
                "aum_difference": None,
                "counts_match": len(table_data) == source_count,
                "aum_matches": False,
                "reconciliation_passed": False,
            }
            for table_name, table_data in table_data_list
        ])

    report_dir = ROOT / "reports" / args.scenario
    report_paths = generate_reports(
        reconciliation=reconciliation,
        validation_errors=validation_errors,
        output_dir=str(report_dir),
    )

    print("\nReconciliation:")
    print(reconciliation.to_string(index=False))

    print("\nReports:")
    for name, path in report_paths.items():
        print(f"- {name}: {path}")

    passed = (
        not validation_errors
        and reconciliation["reconciliation_passed"].all()
    )

    print(f"\nPIPELINE RESULT: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())