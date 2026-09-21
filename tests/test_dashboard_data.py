from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "dashboard"))
from prepare_data import build  # noqa: E402


class SourceReconciliation(unittest.TestCase):
    def test_uploads_match_cached_workbook_controls(self) -> None:
        upload = ROOT.parent / "upload"
        if not upload.exists():
            self.skipTest("Original user uploads are not committed to the public repository")
        frame = build(upload / "GMPP_2024_25.xlsx", upload / "GMPP_2025_26.xlsx")
        actual = frame.groupby("year").agg(records=("project", "size"), cost=("cost_m", "sum"),
                                           missing_cost=("cost_m", lambda x: x.isna().sum()),
                                           missing_duration=("duration_months", lambda x: x.isna().sum()),
                                           unrated=("rating", lambda x: x.isna().sum()))
        for year, expected in {"2024-25": (213, 565707.28, 56, 59, 127),
                               "2025-26": (189, 464052.66, 56, 57, 108)}.items():
            self.assertEqual(tuple(actual.loc[year].round(2)), expected)
        tiers = frame.loc[frame.year.eq("2025-26"), "risk_tier"].value_counts()
        self.assertEqual(tiers.to_dict(), {"Not scored": 108, "Critical": 32, "High": 30, "Medium": 16, "Low": 3})

    def test_deployed_snapshot_has_expected_grain(self) -> None:
        frame = pd.read_csv(ROOT / "dashboard" / "data" / "projects.csv")
        self.assertEqual(frame.groupby("year").size().to_dict(), {"2024-25": 213, "2025-26": 189})
        self.assertEqual(frame.groupby("year").cost_m.sum().round(2).to_dict(),
                         {"2024-25": 565707.28, "2025-26": 464052.66})


if __name__ == "__main__":
    unittest.main()
