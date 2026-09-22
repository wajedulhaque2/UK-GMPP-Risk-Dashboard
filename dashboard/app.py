"""Source-backed UK Government Major Projects portfolio dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
NAVY = "#1A2F45"
TEAL = "#986635"
RATING_COLORS = {"RED": "#B91C1C", "AMBER": "#E9A800", "GREEN": "#087F3E", "Unrated": "#9AA9B5"}
ROW_COLORS = {"RED": ("#B91C1C", "#FFFFFF"), "AMBER": ("#E9A800", "#171717"),
              "GREEN": ("#087F3E", "#FFFFFF")}


@st.cache_data
def load() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "projects.csv")


def chart(fig: go.Figure, height: int = 420, bottom: int = 48) -> None:
    fig.update_layout(
        template="plotly_dark" if dark_mode else "plotly_white", height=height,
        font={"family": "Aptos, Arial", "color": TEXT, "size": 12},
        title={"x": 0.02, "xanchor": "left", "font": {"size": 18, "family": "Arial Narrow, Arial"}},
        margin={"l": 24, "r": 56, "t": 65, "b": bottom},
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, bargap=0.3,
        hoverlabel={"font": {"family": "Arial"}},
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, automargin=True)
    st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar": False})


def bar(frame: pd.DataFrame, x: str, y: str, title: str, *, height: int = 460,
        color: str | None = None, format: str = ",.0f", suffix: str = "", maximum: float | None = None) -> None:
    ordered = frame.sort_values(x)
    fig = px.bar(ordered, x=x, y=y, orientation="h")
    fig.update_traces(marker_color=color or ACCENT, texttemplate=f"%{{x:{format}}}{suffix}", textposition="outside",
                      cliponaxis=False, hovertemplate=f"%{{y}}<br>%{{x:{format}}}{suffix}<extra></extra>")
    fig.update_layout(title=title, showlegend=False)
    fig.update_yaxes(title=None, showgrid=False)
    fig.update_xaxes(title=None, rangemode="tozero")
    if maximum is not None:
        fig.update_xaxes(range=[0, maximum * 1.12])
    chart(fig, height)


st.set_page_config(page_title="UK major projects | portfolio risk", page_icon="📊", layout="wide")
st.sidebar.title("UK major projects")
dark_mode = st.sidebar.toggle("Dark mode", value=False, key="dark_mode")
BACKGROUND, SURFACE, TEXT, MUTED, BORDER, GRID, ACCENT = (
    ("#111D2B", "#203248", "#F4F2EC", "#BDC7CF", "#43566A", "#35485A", "#D2A164")
    if dark_mode else
    ("#F4F1E9", "#FFFEFA", "#1A2F45", "#566A79", "#DAD9D0", "#E8E6DF", TEAL)
)
st.markdown(f"""
<style>
.stApp {{background:{BACKGROUND};color:{TEXT};font-family:Aptos,Arial,sans-serif;}}
[data-testid="stSidebar"] {{background:{SURFACE};border-right:1px solid {BORDER};color:{TEXT};}}
.stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {{color:{TEXT};}}
.stApp [data-testid="stCaptionContainer"] p, [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{color:{MUTED};}}
.stApp h1, .stApp h2, .stApp h3 {{font-family:'Arial Narrow',Arial,sans-serif;text-transform:uppercase;letter-spacing:.035em;}}
[data-testid="stSidebar"] {{border-right:4px solid {ACCENT};}}
[data-testid="stSidebar"] h1 {{font-family:'Arial Narrow',Arial,sans-serif;text-transform:uppercase;letter-spacing:.05em;}}
[data-testid="stMetric"], [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {{background:{SURFACE};border:1px solid {BORDER};border-radius:9px;}}
[data-testid="stMetric"] {{padding:0.85rem 1rem;min-height:115px;border-radius:3px;border-top:4px solid {ACCENT};}}
[data-testid="stMetric"] label, [data-testid="stMetricValue"] {{color:{TEXT};}}
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {{padding:0.35rem;border-radius:3px;}}
[data-testid="stHeader"] {{background:{BACKGROUND};}}
[data-testid="stAlert"] {{color:{TEXT};}}
.scope {{background:{'#2D3C4A' if dark_mode else '#EEE8DA'};border-left:5px solid {ACCENT};padding:0.75rem 1rem;margin:0.5rem 0 1.2rem;color:{TEXT};}}
[data-baseweb="select"] > div, [data-testid="stSidebar"] [role="radiogroup"],
[data-baseweb="input"] > div {{background:{SURFACE};color:{TEXT};border-color:{BORDER};}}
[data-baseweb="select"] *, [data-baseweb="input"] input, [data-testid="stSidebar"] [role="radiogroup"] * {{color:{TEXT};}}
[data-baseweb="popover"] {{background:{SURFACE};color:{TEXT};}}
[data-baseweb="popover"] li {{background:{SURFACE};color:{TEXT};}}
</style>
""", unsafe_allow_html=True)

data = load()
st.sidebar.caption("NISTA annual source data · 2024–26")
view = st.sidebar.radio("View", ["Executive dashboard", "Departments", "Project register", "Data quality", "Methodology"])
st.sidebar.divider()
year = st.sidebar.selectbox("Reporting year", ["2025-26", "2024-25", "Both years"])
department = st.sidebar.selectbox("Department", ["All departments", *sorted(data.department.dropna().unique())])
category = st.sidebar.selectbox("Category", ["All categories", *sorted(data.category.dropna().unique())])

scope = data if year == "Both years" else data.loc[data.year.eq(year)]
if department != "All departments":
    scope = scope.loc[scope.department.eq(department)]
if category != "All categories":
    scope = scope.loc[scope.category.eq(category)]
scope = scope.copy()
scope["rating_label"] = scope.rating.fillna("Unrated")
scope_label = f"{year} · {department} · {category}"

st.title({"Executive dashboard": "Government major projects", "Departments": "Departmental analysis",
          "Project register": "Project risk register", "Data quality": "Source data quality",
          "Methodology": "Methodology and interpretation"}[view])
st.caption("UK Government Major Projects Portfolio · source: NISTA annual project data")
st.markdown(f'<div class="scope">{scope_label}</div>', unsafe_allow_html=True)

if view == "Executive dashboard":
    cards = st.columns(4)
    cards[0].metric("Project records", f"{len(scope):,}")
    cards[1].metric("Whole-life cost with data", f"£{scope.cost_m.sum() / 1000:,.1f}bn")
    cards[2].metric("Rated projects", f"{scope.risk_score.notna().sum():,}")
    cards[3].metric("Critical analytical tier", f"{scope.risk_tier.eq('Critical').sum():,}")
    st.caption("Whole-life cost sums only reported numeric values. Year totals count project-year records; projects appearing in both years are counted twice.")

    rating = scope.groupby(["year", "rating_label"]).size().reset_index(name="Projects")
    risk_counts = scope.risk_tier.value_counts().reindex(["Critical", "High", "Medium", "Low", "Not scored"], fill_value=0)
    mix, tiers = st.columns(2)
    with mix:
        fig = px.bar(rating, x="year", y="Projects", color="rating_label", barmode="stack",
                     category_orders={"year": ["2024-25", "2025-26"], "rating_label": ["RED", "AMBER", "GREEN", "Unrated"]},
                     color_discrete_map=RATING_COLORS)
        fig.update_layout(title="Published delivery ratings", legend_title=None,
                          legend={"orientation": "h", "y": -0.25, "x": 0})
        fig.update_xaxes(title=None, type="category")
        chart(fig, 400, 95)
    with tiers:
        tier_frame = risk_counts.rename_axis("Tier").reset_index(name="Projects")
        fig = px.bar(tier_frame, x="Tier", y="Projects", color="Tier",
                     color_discrete_map={"Critical": "#B91C1C", "High": "#C76622", "Medium": "#D7A225",
                                         "Low": "#087F3E", "Not scored": "#8394A1"}, text="Projects")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(title="Analytical risk tiers", showlegend=False)
        fig.update_xaxes(title=None)
        chart(fig, 400)

    by_department = scope.groupby("department", dropna=False).agg(cost_m=("cost_m", "sum"), projects=("project", "size")).reset_index()
    if len(by_department):
        bar(by_department.nlargest(12, "cost_m"), "cost_m", "department", "Largest whole-life cost exposure by department (£m)",
            height=max(400, min(600, 110 + 34 * min(len(by_department), 12))), format=",.0f")
    st.info("The analytical tier is an independent screening aid. Cost and duration measure exposure, not proof of delivery failure. Unrated projects are not scored.")

elif view == "Departments":
    summary = scope.groupby("department", dropna=False).agg(projects=("project", "size"), cost_m=("cost_m", "sum"),
        rated=("risk_score", "count"), mean_score=("risk_score", "mean"), critical=("risk_tier", lambda x: x.eq("Critical").sum())).reset_index()
    if not summary.empty:
        bar(summary.nlargest(15, "cost_m"), "cost_m", "department", "Whole-life cost by department (£m)",
            height=max(420, min(660, 130 + 32 * min(len(summary), 15))))
        scored = summary.loc[summary.rated.gt(0)]
        if not scored.empty:
            bar(scored, "mean_score", "department", "Average analytical score among rated projects",
                height=max(420, min(660, 130 + 32 * len(scored))), format=".1f", maximum=100,
                color="#77ACDB" if dark_mode else "#416383")
        st.caption("Average scores exclude unrated projects. Compare rated counts before interpreting a department average.")
        st.dataframe(summary.rename(columns={"projects": "Projects", "cost_m": "Cost £m", "rated": "Rated", "mean_score": "Average score", "critical": "Critical"}),
                     width="stretch", hide_index=True)

elif view == "Project register":
    tier = st.selectbox("Analytical tier", ["All tiers", "Critical", "High", "Medium", "Low", "Not scored"])
    register = scope if tier == "All tiers" else scope.loc[scope.risk_tier.eq(tier)]
    st.caption(f"{len(register):,} project-year records in this selection. The score is a custom analytical measure, not an official delivery rating.")
    display = (
        register[["year", "project", "department", "category", "rating", "cost_m", "duration_months", "variance_pct", "risk_score", "risk_tier", "project_id"]]
        .rename(columns={"year": "Year", "project": "Project", "department": "Department", "category": "Category",
                         "rating": "IPA rating", "cost_m": "Whole-life cost £m", "duration_months": "Duration months",
                         "variance_pct": "FY variance %", "risk_score": "Analytical score", "risk_tier": "Tier", "project_id": "Project ID"})
    )
    def rating_row(row: pd.Series) -> list[str]:
        background, foreground = ROW_COLORS.get(row["IPA rating"], (SURFACE, TEXT))
        style = f"background-color: {background}; color: {foreground};"
        return [style] * len(row)

    st.caption("Rows use the published IPA rating: RED, AMBER, or GREEN. Unrated records remain neutral.")
    st.dataframe(display.style.apply(rating_row, axis=1), width="stretch", hide_index=True, height=650)
    st.download_button("Download filtered register", register.to_csv(index=False), "gmpp_filtered_projects.csv", "text/csv")

elif view == "Data quality":
    quality = scope.groupby("year").agg(records=("project", "size"), cost_m=("cost_m", "sum"),
        missing_cost=("cost_m", lambda x: x.isna().sum()), missing_duration=("duration_months", lambda x: x.isna().sum()),
        unrated=("rating", lambda x: x.isna().sum())).reset_index()
    st.dataframe(quality.rename(columns={"year": "Year", "records": "Records", "cost_m": "Reported cost £m",
        "missing_cost": "Missing cost", "missing_duration": "Missing duration", "unrated": "Unrated"}), width="stretch", hide_index=True)
    if not quality.empty:
        melted = quality.melt(id_vars="year", value_vars=["missing_cost", "missing_duration", "unrated"], var_name="Field", value_name="Projects")
        melted["Field"] = melted["Field"].map({"missing_cost": "Cost missing", "missing_duration": "Duration missing", "unrated": "IPA rating missing / exempt"})
        fig = px.bar(melted, x="Projects", y="Field", color="year", barmode="group", orientation="h",
                     color_discrete_map={"2024-25": ACCENT, "2025-26": "#77ACDB" if dark_mode else "#416383"})
        fig.update_layout(title="Unavailable fields by reporting year", legend_title=None,
                          legend={"orientation": "h", "y": -0.25, "x": 0})
        fig.update_yaxes(title=None, showgrid=False)
        chart(fig, 380, 95)
    st.caption("Missing, exempt, planning-stage, and ranged text are preserved as unavailable analytical values unless a Mid estimate is explicitly supplied.")

else:
    st.markdown("""
### Sources and grain
Each record represents a project in one annual NISTA extract. The 2024–25 and 2025–26 uploads contain 213 and 189 project rows respectively. Costs are in **£m, 2024–25 real prices**. The repository contains a derived CSV snapshot and a reproducible extraction script; original annual files are kept outside the repository.

### Analytical risk score (0–100)
The independent score adds delivery confidence (GREEN 5 / AMBER 25 / RED 40), cost exposure (5–25), duration exposure (5–20), and financial-year variance (0–15). Critical: 70–100; High: 50–69; Medium: 30–49; Low: below 30. A project without a usable IPA rating is **Not scored**. Missing cost, duration, or variance contributes zero to the component; its source value remains missing in the register.

### Reading the figures
The score is **not an official NISTA or departmental rating**. A larger project or longer schedule can score higher because it has greater exposure, without evidence of poor management. Financial-year variance is not a whole-life cost overrun. Costs across both years count each reported project-year separately. Exempt text and planning-stage statements are not treated as zero-valued source observations.
""")
