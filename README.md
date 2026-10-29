
# Fund Valuation Data Quality Automation Framework

## 1. Overview

This project implements a Python-based automated testing framework
for validating fund valuation data pipelines.

The framework is designed to validate financial calculations,
data completeness, data quality, deduplication, identifier mapping,
and consistency across pipeline layers.

It uses Python, Pandas, Pytest, and SQL to detect data discrepancies
and generate actionable test reports.

## 2. Objectives

- Validate daily, monthly, yearly, and year-to-date (YTD) metrics.
- Verify data completeness across source, landing, mart, and reporting layers.
- Detect missing, duplicate, malformed, and inconsistent records.
- Validate fund identifier transformations and reference mappings.
- Reconcile record counts and financial aggregates.
- Generate reports containing failed checks and discrepancy details.
- Support repeatable local and CI-driven execution.

## 3. Technology Stack

- Python 3.11 or 3.12
- Pytest
- Pandas
- SQLite and SQL
- pytest-html
- GitHub Actions

## 4. Architecture

External Provider
    -> Source Dataset
    -> Landing Layer
    -> Mart Layer
    -> Final Reporting Layer
    -> Automated Validation
    -> HTML / CSV Reports

The initial implementation uses synthetic datasets and a local
SQLite database to simulate the pipeline layers.

No production database access is required.

## 5. Test Coverage

### Financial Calculations
- Daily, monthly, yearly, and YTD metrics
- Configurable calculation tolerances
- Rounding and precision rules
- Leap years and missing trading days
- Zero denominators where applicable

### Data Completeness and Reconciliation
- Source-to-landing-to-mart-to-reporting comparisons
- Missing funds and valuation records
- Record-count and aggregate reconciliation
- Late-arriving data handling

### Data Quality
- Mandatory-field and NULL checks
- Data type and range validation
- Duplicate detection
- Identifier transformation and reference mapping
- Business-rule validation

### Reporting and Execution
- Pytest execution reports
- CSV reconciliation results
- Failure details and affected records
- CI-driven regression execution

## 6. Assumptions and Scope

- All test data is synthetic and contains no confidential information.
- SQLite represents the pipeline layers in the local implementation.
- Business rules are explicitly documented and configurable.
- AUM formulas and aggregation semantics must be confirmed or
  documented before they are treated as authoritative.
- Numeric tolerances and rounding rules are configurable.
- Late-arriving data is evaluated according to a documented
  processing cutoff and reconciliation policy.
- Production-scale performance and distributed processing are
  outside the initial implementation scope.

## 7. Setup

Create and activate a Python virtual environment, then install
the dependencies:

    python -m venv .venv
    python -m pip install -r requirements.txt

## 8. Execution

Test and execution commands will be documented as the framework
is implemented.

The intended test command is:

    python -m pytest

## 9. Reports

The framework will generate HTML test results and CSV reconciliation
details. Reports will identify the failed rule, affected batch or fund,
and expected versus actual values where applicable.

## 10. Limitations and Future Enhancements

- Integrate with a production-compatible analytical warehouse.
- Add Great Expectations or dbt tests where appropriate.
- Add configurable alerting for critical reconciliation failures.
- Extend execution to large datasets and distributed processing.
- Add historical trend reporting for data-quality metrics.
