from __future__ import annotations

import streamlit as st

from components.charts import bar_rank, pie
from components.filters import current_filters
from components.kpi_cards import kpi_grid
from components.layout import page_note
from components.tables import download_csv, styled_table
from services.optimization_service import opportunity_table, optimization_summary, recommendations


def render() -> None:
    filters = current_filters()
    summary = optimization_summary(filters)
    page_note("Reclaim unused and idle seats before buying more. Recommendations are calculated from the filtered license register.")
    kpi_grid(
        [
            {"label": "Current license spend", "value": summary["current_spend"], "kind": "currency", "help": "Annualized"},
            {"label": "Potential optimized spend", "value": summary["optimized_spend"], "kind": "currency"},
            {"label": "Potential annual savings", "value": summary["annual_savings"], "kind": "currency"},
            {"label": "Optimization %", "value": summary["optimization_pct"], "kind": "percent"},
            {"label": "Never activated / abandoned", "value": summary["unused"], "kind": "int"},
            {"label": "Inactive licenses", "value": summary["underutilized"], "kind": "int"},
            {"label": "Users with overlapping tools", "value": summary["overlap_users"], "kind": "int"},
        ]
    )

    st.subheader("Recommendations")
    for rec in recommendations(filters):
        st.markdown(f'<div class="insight-box insight-attn">{rec}</div>', unsafe_allow_html=True)

    opp = opportunity_table(filters)
    if opp.empty:
        st.info("No optimization opportunities in the current filter.")
        return
    by_type = opp.groupby("opportunity_type", as_index=False).agg(licenses=("license_id", "nunique"), annual_cost=("annual_cost", "sum"))
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(pie(by_type, "opportunity_type", "annual_cost", "Opportunity by type"), width="stretch")
    with c2:
        by_dept = (
            opp.groupby("department_name", as_index=False)["annual_cost"]
            .sum()
            .sort_values("annual_cost", ascending=False)
            .head(12)
        )
        st.plotly_chart(bar_rank(by_dept, "department_name", "annual_cost", "Opportunity by department"), width="stretch")

    stale = opp[opp["days_inactive"] >= 30]
    if not stale.empty:
        buckets = [
            ("30+ days", stale[stale["days_inactive"] >= 30]["annual_cost"].sum()),
            ("60+ days", stale[stale["days_inactive"] >= 60]["annual_cost"].sum()),
            ("90+ days", stale[stale["days_inactive"] >= 90]["annual_cost"].sum()),
        ]
        st.write({k: f"${v:,.0f}" for k, v in buckets})

    styled_table(opp.head(250), height=480)
    download_csv(opp, "license_optimization_opportunities.csv", "Export opportunities")
