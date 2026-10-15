from __future__ import annotations

import streamlit as st

from components.charts import bar_rank, line_trend
from components.filters import current_filters
from components.kpi_cards import kpi_grid
from components.layout import page_note
from components.tables import download_csv, styled_table
from services.metric_service import investment_value_trend, spend_by_dimension
from services.roi_service import portfolio_roi, usecase_roi_table


def render() -> None:
    filters = current_filters()
    r = portfolio_roi(filters)
    page_note("ROI uses realized financial benefit only. Demonstrated productivity is excluded until it is realized.")
    kpi_grid(
        [
            {"label": "Gross benefit", "value": r["gross_benefit"], "kind": "currency"},
            {"label": "Total AI cost", "value": r["total_cost"], "kind": "currency"},
            {"label": "Net benefit", "value": r["net_benefit"], "kind": "currency"},
            {"label": "ROI", "value": r["roi"], "kind": "percent"},
            {"label": "Benefit-cost ratio", "value": r["benefit_cost_ratio"], "kind": "number", "decimals": 2},
            {"label": "Payback", "value": r["payback_months"], "kind": "months"},
            {"label": "Cost / active user", "value": r["cost_per_active_user"], "kind": "currency"},
            {"label": "Cost / AI task", "value": r["cost_per_ai_task"], "kind": "currency"},
            {"label": "Cost / hour saved", "value": r["cost_per_hour_saved"], "kind": "currency"},
            {"label": "Realized / AI user", "value": r["realized_per_user"], "kind": "currency"},
            {"label": "Realized / $1 spend", "value": r["realized_per_dollar"], "kind": "number", "decimals": 2},
        ]
    )
    trend = investment_value_trend(filters)
    if not trend.empty:
        st.plotly_chart(line_trend(trend, "month", ["roi"], "Monthly ROI"), width="stretch")

    bu = spend_by_dimension(filters, "business_unit_name")
    if not bu.empty:
        bu = bu.copy()
        bu["roi"] = (bu["realized_value"] - bu["total_cost"]) / bu["total_cost"].replace(0, 1)
        st.plotly_chart(bar_rank(bu, "business_unit_name", "roi", "ROI by business unit"), width="stretch")

    table = usecase_roi_table(filters)
    if not table.empty:
        show = table[
            [
                "use_case_name",
                "business_unit",
                "status",
                "realized_value",
                "total_cost",
                "net_benefit",
                "roi",
                "bcr",
                "payback_months",
                "classification",
            ]
        ]
        styled_table(show)
        download_csv(table, "use_case_roi.csv")
