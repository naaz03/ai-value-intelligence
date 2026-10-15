from __future__ import annotations

import streamlit as st

from components.charts import bar_rank, line_trend, pie
from components.filters import current_filters
from components.kpi_cards import kpi_grid
from components.layout import page_note
from components.tables import download_csv, styled_table
from services.metric_service import (
    adoption_by_dimension,
    investment_value_trend,
    portfolio_kpis,
    segment_breakdown,
    training_lift,
)


def render() -> None:
    filters = current_filters()
    k = portfolio_kpis(filters)
    page_note("Adoption is necessary but not sufficient for value. Usage is not productivity, and productivity is not cash.")
    kpi_grid(
        [
            {"label": "Eligible employees", "value": k["eligible_users"], "kind": "int"},
            {"label": "Licensed users", "value": k["licensed_users"], "kind": "int"},
            {"label": "Active users", "value": k["active_users"], "kind": "int"},
            {"label": "Adoption rate", "value": k["adoption_rate"], "kind": "percent", "help": "Active / licensed"},
            {"label": "Activation rate", "value": k["activation_rate"], "kind": "percent", "help": "Licensed / eligible"},
            {"label": "Underutilized licenses", "value": k["underutilized_licenses"], "kind": "int"},
        ]
    )
    trend = investment_value_trend(filters)
    if not trend.empty:
        st.plotly_chart(line_trend(trend, "month", ["active_users", "licensed_users"], "Licensed vs active users"), width="stretch")

    segments = segment_breakdown(filters)
    c1, c2 = st.columns(2)
    with c1:
        if not segments.empty:
            st.plotly_chart(pie(segments, "segment", "licenses", "User segments"), width="stretch")
    with c2:
        lift = training_lift(filters)
        if not lift.empty:
            st.plotly_chart(bar_rank(lift, "ai_training_completed", "sessions", "Average sessions after training"), width="stretch")
            st.caption("Employees who completed training generally show higher session depth.")

    if not segments.empty:
        styled_table(segments)
        download_csv(segments, "user_segments.csv")

    tabs = st.tabs(["Department", "Business unit", "Country", "Job level", "AI product"])
    dims = ["department_name", "business_unit_name", "country", "job_level", "product_name"]
    for tab, dim in zip(tabs, dims):
        with tab:
            frame = adoption_by_dimension(filters, dim)
            if frame.empty:
                st.write("No adoption records for this cut.")
                continue
            st.plotly_chart(bar_rank(frame.head(20), dim, "adoption_rate", f"Adoption by {dim.replace('_',' ')}"), width="stretch")
            styled_table(frame)
            download_csv(frame, f"adoption_by_{dim}.csv")
