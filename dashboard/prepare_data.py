"""Extract an auditable project snapshot from the two NISTA annual workbooks.

Supports both Strict OOXML (2024-25) and Transitional OOXML (2025-26).
Run: python dashboard/prepare_data.py PATH_2024_25.xlsx PATH_2025_26.xlsx
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pandas as pd


OUT = Path(__file__).resolve().parent / "data" / "projects.csv"
FIELDS = {
    "Project Name": "project",
    "Department": "department",
    "Annual Report Category": "category",
    "IPA Delivery Confidence Assessment": "rating_raw",
    "Start Date": "start_raw",
    "End Date": "end_raw",
    "Financial Year Variance (%)": "variance_raw",
}


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def read_workbook(path: Path) -> pd.DataFrame:
    """Read worksheet rows without relying on the workbook's OOXML flavour."""
    with ZipFile(path) as archive:
        strings = ["".join(node.itertext()) for node in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = [node.get("name") for node in workbook.iter() if _local(node.tag) == "sheet"]
        sheet_number = 1 if len(sheets) == 1 else 2  # 2025-26 has a README before the data.
        root = ET.fromstring(archive.read(f"xl/worksheets/sheet{sheet_number}.xml"))
        rows = []
        for row in root.findall(".//{*}sheetData/{*}row"):
            cells = {}
            for cell in row:
                address = cell.get("r", "")
                col = 0
                for letter in re.match(r"[A-Z]+", address).group():
                    col = col * 26 + ord(letter) - ord("A") + 1
                value = cell.findtext("{*}v")
                if cell.get("t") == "s" and value is not None:
                    value = strings[int(value)]
                if cell.get("t") == "inlineStr":
                    value = "".join(cell.itertext())
                cells[col - 1] = value
            rows.append([cells.get(i) for i in range(21)])
    frame = pd.DataFrame(rows[1:], columns=rows[0])
    if len(frame) not in (213, 189) or frame.columns[0] != "Project Name":
        raise ValueError(f"Unexpected annual data shape in {path}: {frame.shape}")
    return frame


def number(value: object) -> float | None:
    if value is None:
        return None
    raw = str(value).replace(",", "").replace("£", "").strip()
    if re.fullmatch(r"-?\d+(?:\.\d+)?%?", raw):
        return float(raw.rstrip("%"))
    middle = re.search(r"\bMid\s*:\s*£?\s*(-?[\d,]+(?:\.\d+)?)", str(value), re.I)
    return float(middle.group(1).replace(",", "")) if middle else None


def date(value: object) -> datetime | None:
    if value is None:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(value).strip(), fmt)
        except ValueError:
            pass
    return None


def clean(frame: pd.DataFrame, year: str) -> pd.DataFrame:
    result = frame[list(FIELDS)].rename(columns=FIELDS).copy()
    result["year"] = year
    result["project_id"] = frame["GMPP ID" if year == "2024-25" else "Major Projects ID"]
    cost_column = next(c for c in frame if c.startswith("Whole Life Cost (£m"))
    result["cost_m"] = frame[cost_column].map(number)
    result["variance_pct"] = result["variance_raw"].map(number)
    start = result["start_raw"].map(date)
    end = result["end_raw"].map(date)
    result["duration_months"] = [(e - s).days / 30.44 if s and e and e >= s else None for s, e in zip(start, end)]
    result["rating"] = result["rating_raw"].astype("string").str.upper().str.strip().where(
        lambda values: values.isin(["RED", "AMBER", "GREEN"])
    )
    result["department"] = result["department"].astype("string").str.strip().str.upper()
    result["delivery_score"] = result["rating"].map({"RED": 40, "AMBER": 25, "GREEN": 5})
    result["cost_score"] = result["cost_m"].map(
        lambda x: 0 if pd.isna(x) else 5 if x < 100 else 10 if x < 500 else 15 if x < 1000 else 20 if x < 5000 else 25
    )
    result["duration_score"] = result["duration_months"].map(
        lambda x: 0 if pd.isna(x) else 5 if x < 36 else 10 if x < 60 else 15 if x < 120 else 20
    )
    result["variance_score"] = result["variance_pct"].map(
        lambda x: 0 if pd.isna(x) or x <= 0 else 5 if x < 10 else 10 if x < 20 else 15
    )
    result["risk_score"] = result[["delivery_score", "cost_score", "duration_score", "variance_score"]].sum(axis=1, min_count=4)
    result["risk_tier"] = result["risk_score"].map(
        lambda x: "Not scored" if pd.isna(x) else "Critical" if x >= 70 else "High" if x >= 50 else "Medium" if x >= 30 else "Low"
    )
    result["source_file"] = f"GMPP_{year.replace('-', '_')}.xlsx"
    return result.drop(columns=["start_raw", "end_raw", "variance_raw", "rating_raw"])


def build(first: Path, second: Path) -> pd.DataFrame:
    frame = pd.concat([clean(read_workbook(first), "2024-25"), clean(read_workbook(second), "2025-26")], ignore_index=True)
    if frame.groupby("year").size().to_dict() != {"2024-25": 213, "2025-26": 189}:
        raise ValueError("Annual source counts did not match the workbook")
    return frame


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = build(Path(sys.argv[1]), Path(sys.argv[2]))
    data.to_csv(OUT, index=False)
    print(data.groupby("year").agg(projects=("project", "size"), cost_m=("cost_m", "sum"), scored=("risk_score", "count")))
