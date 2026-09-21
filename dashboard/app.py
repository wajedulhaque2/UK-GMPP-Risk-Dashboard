"""Source-backed UK Government Major Projects portfolio dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
NAVY = "#16324A"
TEAL = "#147D83"
COLORS = {"Critical": "#A43D3D", "High": "#C47730", "Medium": "#D8AC4C", "Low": "#5F9A84", "Not scored": "#ABB9C3"}
RATING_COLORS = {"RED": "#A43D3D", "AMBER": "#D7A745", "GREEN": "#4C9272", "Unrated": "#ABB9C3"}


@st.cache_data
def load() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "projects.csv")


def chart(fig: go.Figure, height: int = 420, bottom: int = 48) -> None:
    fig.update_layout(
        template="plotly_white", height=height, font={"family": "Arial", "color": NAVY, "size": 12},
        title={"x": 0.02, "xanchor": "left", "font": {"size": 18}},
        margin={"l": 24, "r": 56, "t": 65, "b": bottom},
        paper_bgcolor="white", plot_bgcolor="white", bargap=0.3,
        hoverlabel={"font": {"family": "Arial"}},
    )
    fig.update_xaxes(gridcolor="#E5EBEF", zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor="#E5EBEF", zeroline=False, automargin=True)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def bar(frame: pd.DataFrame, x: str, y: str, title: str, *, height: int = 460,
        color: str = TEAL, format: str = ",.0f", suffix: str = "", maximum: float | None = None) -> None:
    ordered = frame.sort_values(x)
    fig = px.bar(ordered, x=x, y=y, orientation="h")
    fig.update_traces(marker_color=color, texttemplate=f"%{{x:{format}}}{suffix}", textposition="outside",
                      cliponaxis=False, hovertemplate=f"%{{y}}<br>%{{x:{format}}}{suffix}<extra></extra>")
    fig.update_layout(title=title, showlegend=False)
    fig.update_yaxes(title=None, showgrid=False)
    fig.update_xaxes(title=None, rangemode="tozero")
    if maximum is not None:
        fig.update_xaxes(range=[0, maximum * 1.12])
    chart(fig, height)


st.set_page_config(page_title="UK major projects | portfolio risk", page_icon="📊", layout="wide")
st.markdown("""
<style>
.stApp {background:#F5F8FA}
[data-testid="stSidebar"] {background:white;border-right:1px solid #DCE6EA}
[data-testid="stMetric"] {background:white;border:1px solid #DCE6EA;border-radius:9px;padding:0.85rem 1rem;min-height:115px}
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {background:white;border:1px solid #E0E8EB;border-radius:9px;padding:0.35rem}
.scope {background:#E7F2F2;border-left:4px solid #147D83;padding:0.75rem 1rem;margin:0.5rem 0 1.2rem;color:#24424E}
</style>
""", unsafe_allow_html=True)

data = load()
st.sidebar.title("UK major projects")
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
    fig = px.bar(rating, x="year", y="Projects", color="rating_label", barmode="stack",
                 category_orders={"year": ["2024-25", "2025-26"], "rating_label": ["RED", "AMBER", "GREEN", "Unrated"]},
                 color_discrete_map=RATING_COLORS)
    fig.update_layout(title="Published delivery-confidence availability", legend_title=None,
                      legend={"orientation": "h", "y": -0.25, "x": 0})
    fig.update_xaxes(title=None, type="category")
    chart(fig, 420, 95)

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
                height=max(420, min(660, 130 + 32 * len(scored))), format=".1f", maximum=100, color="#416383")
        st.caption("Average scores exclude unrated projects. Compare rated counts before interpreting a department average.")
        st.dataframe(summary.rename(columns={"projects": "Projects", "cost_m": "Cost £m", "rated": "Rated", "mean_score": "Average score", "critical": "Critical"}),
                     width="stretch", hide_index=True)

elif view == "Project register":
    tier = st.selectbox("Analytical tier", ["All tiers", "Critical", "High", "Medium", "Low", "Not scored"])
    register = scope if tier == "All tiers" else scope.loc[scope.risk_tier.eq(tier)]
    st.caption(f"{len(register):,} project-year records in this selection. The score is a custom analytical measure, not an official delivery rating.")
    st.dataframe(register[["year", "project", "department", "category", "rating", "cost_m", "duration_months", "variance_pct", "risk_score", "risk_tier", "project_id"]]
                 .rename(columns={"year": "Year", "project": "Project", "department": "Department", "category": "Category",
                                  "rating": "IPA rating", "cost_m": "Whole-life cost £m", "duration_months": "Duration months",
                                  "variance_pct": "FY variance %", "risk_score": "Analytical score", "risk_tier": "Tier", "project_id": "Project ID"}),
                 width="stretch", hide_index=True, height=650)
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
                     color_discrete_map={"2024-25": TEAL, "2025-26": "#416383"})
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
