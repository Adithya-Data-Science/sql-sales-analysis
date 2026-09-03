# Community Engagement Dashboard and Impact Reporting

This project documents a one-page Excel dashboard and a three-page analytical report created to summarize a university community-engagement program for stakeholders.

## Reporting scope

The dashboard tracks five KPI areas:

1. Participants by department
2. Partnerships by type
3. Average satisfaction by impact area
4. Total funding by impact area
5. Student volunteers

The final reporting package uses a pie chart for partnership composition and a line chart for trends over time. PivotTables, XLOOKUP, data validation, and charts support repeatable updates and quality checks.

## Repository contents

- `data_dictionary.csv` defines the expected input fields.
- `validation_checklist.md` documents the data-quality and refresh process.
- The institutional source workbook is not committed because it may contain internal program records. The résumé reports only aggregate structure and deliverables, not confidential values.

## Workflow

1. Standardize department, partnership type, and impact-area labels.
2. Validate required fields and flag missing satisfaction or funding values.
3. Refresh PivotTables for each KPI area.
4. Use XLOOKUP to map standardized categories and reporting labels.
5. Refresh the dashboard charts and reconcile totals to the cleaned source table.
6. Export the dashboard and accompanying report for stakeholder review.

## Responsible use

This repository intentionally excludes personally identifiable information and internal university records. It demonstrates the reporting design, field definitions, and validation controls without exposing protected data.
