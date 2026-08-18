# Formula, Query & Model Guide

## 1. Power Query architecture

The workbook contains the following named query connections:

| Query | Purpose |
|---|---|
| `stg_GMPP_2024_25` | Stage and standardise the 2024-25 annual source file |
| `stg_GMPP_2025_26` | Stage and standardise the 2025-26 annual source file |
| `fact_GMPP_AllYears` | Append the annual datasets into the analytical fact table |
| `risk_ProjectRegister` | Produce the project-level cleaned risk-register output |
| `dim_Department` | Department dimension used by the Data Model |
| `dim_ReportingYear` | Reporting-year dimension used by the Data Model |

The methodology sheet documents the principal transformation rules:

- department text is trimmed, cleaned and standardised to uppercase;
- reporting year is added during import;
- valid UK-format start/end dates are converted to dates;
- duration months is calculated from cleaned dates using days / 30.44;
- whole-life cost and benefits retain numeric values and use midpoint values where a Low/Mid/High range is supplied;
- IPA ratings are standardised to `RED`, `AMBER` or `GREEN`;
- missing/exempt values are retained in original text fields and represented as null analytically.

## 2. Analytical risk score

The workbook's project register contains separate component scores and a total score:

```text
Delivery Risk Score
+ Cost Exposure Score
+ Duration Exposure Score
+ Variance Risk Score
= Total Risk Score
```

### Delivery-confidence component

```text
GREEN -> 5
AMBER -> 25
RED   -> 40
```

### Whole-life cost component

```text
< £100m       -> 5
£100m-£500m   -> 10
£500m-£1bn    -> 15
£1bn-£5bn     -> 20
£5bn+         -> 25
```

### Duration component

```text
< 3 years     -> 5
3-5 years     -> 10
5-10 years    -> 15
10+ years     -> 20
```

### Financial-year variance component

```text
0% or lower   -> 0
above 0%      -> 5
10% or above  -> 10
20% or above  -> 15
```

### Risk tiers

```text
70-100  -> Critical
50-69   -> High
30-49   -> Medium
<30     -> Low
No usable IPA rating -> Not scored
```

## 3. Data Model measures used by PivotTables

The workbook's PivotTables expose Data Model measures including:

- `Project Count`
- `Total Whole-Life Cost £m`
- `Average Risk Score`
- `Red or Amber % of Rated Projects`

These measures drive the executive, risk-summary and departmental views. The workbook also uses ordinary PivotTable aggregations such as `Count of Project Name` and `Sum of Whole Life Cost Clean` for data-quality validation.

## 4. Pivot Support worksheet formulas

The `Pivot Support` sheet supplements PivotTables with worksheet formulas for dashboard-ready extracts.

### Department rating matrix

Representative formula:

```excel
=COUNTIFS(
 'Project Risk Register'!$B$2:$B$190,$M2,
 'Project Risk Register'!$I$2:$I$190,N$1
)
```

This counts projects for the department in column M by delivery rating in row 1.

### Ranked high-risk project extract

The workbook uses dynamic-array logic built from `FILTER`, `CHOOSE` and `SORTBY` to return project names and risk scores sorted by analytical risk and then cost exposure. The cached workbook preserves the resulting ranked list for reviewers.

## 5. Data-quality controls

The `Data Quality` worksheet validates record counts, total whole-life cost and missing-data coverage by year. Cached values include:

```text
2024-25 records: 213
2025-26 records: 189
Total records:   402
```

Coverage measures shown in the workbook include:

```text
Cost data coverage %
Duration data coverage %
Missing cost projects
Missing duration projects
Unrated projects
```

## 6. Refresh sequence

1. Place annual NISTA source CSVs in the established source-data folder.
2. Do not manually edit the source files.
3. Open Excel and choose `Data -> Refresh All`.
4. Confirm the `Data Quality` sheet returns 213 rows for 2024-25 and 189 rows for 2025-26.
5. Check slicers, PivotTables and PivotCharts update successfully.
6. Review the project register for unexpected nulls or rating changes before relying on dashboard output.

## 7. Important modelling caveat

The custom score is a prioritisation aid only. Cost and duration are exposure variables, not performance verdicts, and the analytical score should not be described as an official NISTA/IPA risk rating.