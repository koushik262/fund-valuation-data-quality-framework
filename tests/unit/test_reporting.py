import pandas as pd

from fund_quality.reporting import generate_reports


def test_generate_reports_creates_csv_and_html(tmp_path):
    reconciliation = pd.DataFrame(
        [
            {
                "table": "landing",
                "record_count": 10,
                "reconciliation_passed": True,
            }
        ]
    )

    validation_errors = [
        {
            "record_id": "REC-1",
            "check": "AUM",
            "error": "AUM mismatch",
        }
    ]

    paths = generate_reports(
        reconciliation,
        validation_errors,
        output_dir=str(tmp_path),
    )

    assert paths["reconciliation_csv"].exists()
    assert paths["validation_errors_csv"].exists()
    assert paths["html_report"].exists()

    html = paths["html_report"].read_text(encoding="utf-8")
    assert "Fund Valuation Data Quality Report" in html
    assert "Overall status: FAIL" in html
    assert "AUM mismatch" in html