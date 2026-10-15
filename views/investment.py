from __future__ import annotations

import streamlit as st

from components.charts import bar_rank, line_trend, pie
from components.filters import current_filters
from components.kpi_cards import kpi_grid
from components.layout import page_note
from components.tables import download_csv, styled_table
from services.metric_service import cost_category_breakdown, enterprise_mart, portfolio_kpis, spend_by_dimension, usecase_mart


def render() -> None:
    filters = current_filters()
    k = portfolio_kpis(filters)
    page_note("Total AI cost includes licensing, infrastructure, implementation, training, support, security, and governance.")
    kpi_grid(
        [
            {"label": "Total AI investment", "value": k["total_cost"], "kind": "currency"},
            {"label": "License-related cost", "value": usecase_mart(filters)["license_cost"].sum() if not usecase_mart(filters).empty else 0, "kind": "currency"},
            {"label": "Infrastructure cost", "value": k["infrastructure_cost"], "kind": "currency"},
            {"label": "Cost per active user", "value": k["cost_per_active_user"], "kind": "currency"},
        ]
    )
    trend = enterprise_mart(filters)
    if not trend.empty:
        st.plotly_chart(line_trend(trend, "month", ["total_cost", "license_cost", "infrastructure_cost"], "Cost trend"), width="stretch")

    cats = cost_category_breakdown(filters)
    c1, c2 = st.columns(2)
    with c1:
        if not cats.empty:
            st.plotly_chart(pie(cats, "cost_category", "amount", "Spend by cost category"), width="stretch")
    with c2:
        if not cats.empty:
            st.plotly_chart(bar_rank(cats, "cost_category", "amount", "Cost drivers"), width="stretch")
            top = cats.iloc[0]
            st.info(f"Largest cost driver: {top['cost_category']} at the selected filters.")

    tabs = st.tabs(["Product", "Vendor", "Business unit", "Department", "Use case"])
    dims = ["product_name", "vendor", "business_unit_name", "department_name", "use_case_name"]
    for tab, dim in zip(tabs, dims):
        with tab:
            frame = spend_by_dimension(filters, dim)
            if frame.empty:
                st.write("No cost records for this cut.")
                continue
            st.plotly_chart(bar_rank(frame.head(15), dim, "total_cost", f"Spend by {dim.replace('_', ' ')}"), width="stretch")
            styled_table(frame.head(25))
            download_csv(frame, f"spend_by_{dim}.csv")
