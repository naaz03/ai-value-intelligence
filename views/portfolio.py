from __future__ import annotations

import streamlit as st

from components.charts import bubble, pie
from components.filters import current_filters
from components.kpi_cards import kpi_grid
from components.layout import page_note
from components.tables import download_csv, format_money_columns, format_pct_columns, styled_table
from services.metric_service import portfolio_kpis, usecase_performance


def render() -> None:
    filters = current_filters()
    k = portfolio_kpis(filters)
    page_note("Classify the registry on evidence: Scale, Optimize, Monitor, Reassess, or Stop. High adoption alone is not a scale signal.")
    kpi_grid(
        [
            {"label": "Production / scaling", "value": k["production_use_cases"], "kind": "int"},
            {"label": "Scale candidates", "value": k["high_performing"], "kind": "int"},
            {"label": "Reassess / stop", "value": k["underperforming"], "kind": "int"},
            {"label": "Realized value", "value": k["realized_value"], "kind": "currency"},
        ]
    )
    perf = usecase_performance(filters)
    if perf.empty:
        st.warning("No use cases in the current filter.")
        return
    cls = perf.groupby("classification", as_index=False).size().rename(columns={"size": "use_cases"})
    st.plotly_chart(pie(cls, "classification", "use_cases", "Portfolio actions"), width="stretch")

    bubble_src = perf.copy()
    bubble_src["investment"] = bubble_src["total_cost"].clip(lower=1)
    st.plotly_chart(
        bubble(bubble_src, "realized_value", "roi", "investment", "classification", "use_case_name", "Value vs ROI (bubble = investment)"),
        width="stretch",
    )

    show = perf[
        [
            "use_case_name",
            "business_owner",
            "department",
            "status",
            "classification",
            "risk_rating",
            "total_cost",
            "potential_value",
            "demonstrated_value",
            "realized_value",
            "roi",
            "payback_months",
            "value_realization_pct",
        ]
    ].copy()
    show = format_pct_columns(format_money_columns(show, ["total_cost", "potential_value", "demonstrated_value", "realized_value"]), ["roi", "value_realization_pct"])
    styled_table(show, height=520)
    download_csv(perf, "use_case_registry.csv", "Export registry")
