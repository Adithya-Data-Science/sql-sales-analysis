# Community Engagement Dashboard and Impact Reporting

This project documents a one-page Excel dashboard and a three-page analytical report created to summarize a university community-engagement program for stakeholders.

## Purpose and reporting outcome

The purpose was to replace separate program measures with one consistent view of participation, partnerships, satisfaction, funding, and volunteer activity. The dashboard and report organize five KPI areas for stakeholder review, while documented validation controls make each refresh traceable. Because the institutional records are private, this repository uses a sanitized sample and publishes the workflow rather than confidential program totals.

## Reporting scope

1. Participants by department
2. Partnerships by type
3. Average satisfaction by impact area
4. Total funding by impact area
5. Student volunteers

The reporting package uses a pie chart for partnership composition and a line chart for trends over time. PivotTables, XLOOKUP, data validation, and charts support repeatable updates and quality checks.

## Repository contents

- `analysis.py` reproduces the KPI summaries and two charts using sanitized input.
- `sample_data.csv` provides a privacy-safe test fixture.
- `data_dictionary.csv` defines the expected fields.
- `validation_checklist.md` documents the quality and refresh process.
- The institutional source workbook is not committed.

## Verified workflow

The sample pipeline was executed successfully and generated department, partnership, satisfaction, funding, and volunteer summaries plus the expected pie and line charts. The published verification demonstrates the workflow without representing synthetic values as real university results.

## Responsible use

This repository excludes personally identifiable information and internal university records. It demonstrates the reporting design, field definitions, and validation controls without exposing protected data.
