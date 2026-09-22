from __future__ import annotations

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"


class ThemeAndRatingTest(unittest.TestCase):
    def test_both_modes_render_and_rows_keep_saturated_rating_colors(self) -> None:
        app = AppTest.from_file(str(APP), default_timeout=20).run()
        self.assertFalse(app.exception)
        self.assertFalse(app.toggle[0].value)

        for dark in (False, True):
            app.toggle[0].set_value(dark).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.toggle[0].value, dark)
            app.radio[0].set_value("Project register").run()
            self.assertFalse(app.exception)
            styles = app.dataframe[0].proto.arrow_data.styler.styles
            for fill, foreground in (("#B91C1C", "#FFFFFF"), ("#E9A800", "#171717"),
                                     ("#087F3E", "#FFFFFF")):
                self.assertIn(f"background-color: {fill}; color: {foreground}", styles)
            self.assertIn("background-color: #203248; color: #F4F2EC" if dark else
                          "background-color: #FFFEFA; color: #1A2F45", styles)


if __name__ == "__main__":
    unittest.main()
