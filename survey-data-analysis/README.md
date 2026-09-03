# Object-Oriented Survey Analytics and Stakeholder Reporting

This reproducible Python application converts survey-style records into validated stakeholder reporting. It uses separate classes for data ingestion and validation, KPI analysis, and output generation so each responsibility can be tested and reused independently.

## Verified outcome

On the published eight-response synthetic fixture, the application:

- detected one missing satisfaction value without discarding the response;
- produced four stakeholder KPIs: 87.5% completion, 3.86/5 average satisfaction, 71.4% positive responses, and eight total responses; and
- generated three presentation-ready charts plus a machine-readable JSON summary.

The tests also prove that duplicate response IDs and satisfaction values outside the 1-to-5 scale stop the workflow instead of silently distorting results.

## Object-oriented design

- `SurveySchema` centralizes required fields and reporting thresholds.
- `SurveyDataValidator` loads, standardizes, and validates records.
- `SurveyKPIAnalyzer` calculates the four stakeholder KPIs.
- `StakeholderReportGenerator` writes the JSON summary and three charts.
- `SurveyReportingApplication` coordinates the end-to-end workflow.

## Run

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python survey_analysis.py sample_survey.csv results
pytest -q
```

`sample_survey.csv` is synthetic and contains no personal information. Original research or institutional survey records are not published.
