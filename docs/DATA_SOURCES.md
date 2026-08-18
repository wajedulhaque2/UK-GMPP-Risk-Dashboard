# Data Sources

## Primary source

**NISTA Major Projects Annual Report dataset**

- Reporting periods in workbook: **2024-25** and **2025-26**
- Grain: one row per project per reporting period
- Whole-life cost unit: **£ millions, presented in 2024-25 real prices**
- Refresh method: Power Query

## Source handling rules

The workbook preserves original text where the source contains exemptions, planning-stage notes or ranges, while creating separate cleaned fields for quantitative analysis.

Key cleaning choices include:

- uppercase standardised department names for relationships;
- cleaned date fields for schedule analysis;
- midpoint treatment for Low/Mid/High cost ranges;
- standardised `RED` / `AMBER` / `GREEN` delivery-confidence values;
- null analytical values where the source is missing or exempt rather than inventing zeros.

## Cached-copy note

The repository workbook is intended to remain reviewable without the original source folder. A refresh requires the annual source CSVs and the local Power Query path configuration used by the model.