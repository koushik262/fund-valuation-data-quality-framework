from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


def generate_reports(
    reconciliation: pd.DataFrame,
    validation_errors: list[dict],
    output_dir: str = "reports",
) -> dict[str, Path]:
    """Write reconciliation and validation results to CSV and HTML files."""
    report_dir = Path(output_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    reconciliation_path = report_dir / "reconciliation_report.csv"
    errors_path = report_dir / "validation_errors.csv"
    html_path = report_dir / "data_quality_report.html"

    reconciliation.to_csv(reconciliation_path, index=False)

    errors = pd.DataFrame(
        validation_errors,
        columns=["record_id", "check", "error"],
    )
    errors.to_csv(errors_path, index=False)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    reconciliation_html = reconciliation.to_html(
        index=False,
        escape=True,
        border=0,
        classes="report-table",
    )
    errors_html = errors.to_html(
        index=False,
        escape=True,
        border=0,
        classes="report-table",
    )

    passed = (
        bool(reconciliation["reconciliation_passed"].all())
        if not reconciliation.empty
        else False
    )
    passed_checks = int(reconciliation["reconciliation_passed"].sum())
    total_checks = len(reconciliation)

    status = "PASS" if passed and errors.empty else "FAIL"

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fund Valuation Data Quality Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; color: #222; }}
h1, h2 {{ color: #17365d; }}
.report-table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; }}
.report-table th, .report-table td {{
    border: 1px solid #ddd; padding: 0.6rem; text-align: left;
}}
.report-table th {{ background: #f1f4f8; }}
.status {{ font-weight: bold; }}
</style>
</head>
<body>
<h1>Fund Valuation Data Quality Report</h1>
<p>Generated: {generated_at}</p>
<p class="status">Overall status: {status}</p>
<p>Reconciliation layers passed: {passed_checks} of {total_checks}</p>
<h2>Pipeline Reconciliation</h2>
{reconciliation_html}
<h2>Validation Errors</h2>
<p>Total validation errors: {len(errors)}</p>
{errors_html}
</body>
</html>
"""

    html_path.write_text(html, encoding="utf-8")

    return {
        "reconciliation_csv": reconciliation_path,
        "validation_errors_csv": errors_path,
        "html_report": html_path,
    }