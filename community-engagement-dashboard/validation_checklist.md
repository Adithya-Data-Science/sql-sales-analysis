# Dashboard refresh and validation checklist

## Before refresh

- Confirm each `record_id` is present and unique.
- Standardize department, partnership-type, and impact-area values.
- Review blank satisfaction, funding, and volunteer fields.
- Confirm satisfaction values fall between 1 and 5.
- Confirm funding and volunteer values are not negative.

## During refresh

- Refresh all PivotTables from the cleaned source table.
- Reconcile participant and partnership totals to the source record count.
- Verify XLOOKUP mappings do not return missing values.
- Confirm the pie chart categories sum to the partnership total.
- Confirm the line chart uses consistent reporting periods.

## Before distribution

- Review KPI labels, filters, and reporting dates.
- Check that only aggregate results appear in exported materials.
- Record the refresh date and any unresolved data limitations.
