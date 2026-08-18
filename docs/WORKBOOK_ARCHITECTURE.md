# Workbook Architecture

## Logical model

```text
NISTA annual CSVs
        |
        v
Power Query staging
stg_GMPP_2024_25 / stg_GMPP_2025_26
        |
        v
fact_GMPP_AllYears
        |
        +--------------------+
        |                    |
        v                    v
dim_Department        dim_ReportingYear
        |                    |
        +---------+----------+
                  |
                  v
          Excel Data Model
                  |
        +---------+---------+
        |                   |
        v                   v
risk_ProjectRegister     DAX measures
        |                   |
        +---------+---------+
                  |
                  v
     PivotTables / PivotCharts
                  |
                  v
          Executive Dashboard
```

## Worksheet roles

- `README` - start here, refresh instructions, model disclaimer.
- `Executive Dashboard` - headline portfolio KPIs and high-level visual analysis.
- `Departmental Analysis` - department-level cost, risk and duration comparison.
- `Project Risk Register` - transformed project-level analytical output.
- `Risk Summary` - risk-tier counts, average scores and cost exposure.
- `Data Quality` - refresh validation and coverage checks.
- `Methodology` - source, cleaning, risk scoring and limitations.
- `Pivot Support` - hidden/supporting PivotTables and formula extracts.

## Separation of concerns

The workbook does not duplicate raw CSV data into a large `Raw Data` worksheet. Instead, raw/staging work is handled by Power Query and the Data Model. The visible project register is the cleaned analytical output. This keeps the portfolio file usable while still exposing the logic, methodology and validation layers needed for auditability.