# Survey Data Analysis and Stakeholder Reporting

This reproducible project cleans survey-style data, validates response ranges, summarizes four KPIs, and produces three presentation-ready visualizations.

## Purpose and verified result

The project prevents incomplete, duplicated, or invalid responses from silently distorting stakeholder conclusions. It separates validation from reporting, then calculates response count, completion rate, average satisfaction, and positive-response rate. On the published synthetic test fixture, the workflow correctly detected one missing satisfaction response and produced all four KPI outputs and three charts.

## What the workflow demonstrates

- Missing-value and duplicate-response checks
- Standardization of categorical responses
- Validation of satisfaction values on a 1-to-5 scale
- KPI reporting for response count, completion rate, average satisfaction, and positive-response rate
- Department, satisfaction, and response-channel visualizations
- Machine-readable summary output for reporting or dashboard refreshes

`sample_survey.csv` is synthetic and contains no personal information. The original graduate-research data is not published.

## Run

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python survey_analysis.py sample_survey.csv results
```

The script stops if response IDs are missing or duplicated or if satisfaction values fall outside the expected range. The committed `results/summary.json` records the verified sample output.
