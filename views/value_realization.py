from __future__ import annotations

import streamlit as st

from components.charts import bar_rank, funnel, waterfall
from components.filters import current_filters
from components.kpi_cards import kpi_grid
from components.layout import page_note
from components.tables import download_csv, styled_table
from services.metric_service import portfolio_kpis, spend_by_dimension, usecase_mart, value_bridge


def render() -> None:
    filters = current_filters()
    k = portfolio_kpis(filters)
    page_note(
        "Potential is theoretical. Demonstrated is evidenced operationally. Realized is captured by the enterprise "
        "and only partly finance-validated."
    )
    kpi_grid(
        [
            {"label": "Potential value", "value": k["potential_value"], "kind": "currency"},
            {"label": "Demonstrated value", "value": k["demonstrated_value"], "kind": "currency"},
            {"label": "Realized value", "value": k["realized_value"], "kind": "currency"},
            {"label": "Value leakage", "value": k["potential_value"] - k["realized_value"], "kind": "currency"},
            {"label": "P→D conversion", "value": k["pd_conversion"], "kind": "percent"},
            {"label": "D→R conversion", "value": k["dr_conversion"], "kind": "percent"},
            {"label": "Overall realization", "value": k["value_realization_pct"], "kind": "percent"},
            {"label": "Finance validated", "value": k["finance_validated"], "kind": "currency"},
            {"label": "Unvalidated realized", "value": k["unvalidated_value"], "kind": "currency"},
            {"label": "Net AI value", "value": k["net_benefit"], "kind": "currency"},
        ]
    )
    bridge = value_bridge(filters)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(waterfall(bridge, "Value realization waterfall"), width="stretch")
    with c2:
        st.plotly_chart(
            funnel(
                [
                    ("Potential", k["potential_value"]),
                    ("Demonstrated", k["demonstrated_value"]),
                    ("Realized", k["realized_value"]),
                ],
                "Value leakage funnel",
            ),
            width="stretch",
        )

    uc = usecase_mart(filters)
    if not uc.empty:
        by_type = (
            uc.groupby("benefit_type", as_index=False)
            .agg(
                potential_value=("potential_value", "sum"),
                demonstrated_value=("demonstrated_value", "sum"),
                realized_value=("realized_value", "sum"),
            )
            .sort_values("realized_value", ascending=False)
        )
        st.plotly_chart(bar_rank(by_type, "benefit_type", "realized_value", "Realized value by benefit type"), width="stretch")
        styled_table(by_type)
        download_csv(by_type, "benefits_by_type.csv", "Export benefit register summary")

    bu = spend_by_dimension(filters, "business_unit_name")
    if not bu.empty:
        st.subheader("Realization by business unit")
        bu = bu.copy()
        bu["realization"] = bu["realized_value"] / bu["potential_value"].replace(0, 1)
        styled_table(bu)
        download_csv(uc, "financial_benefit_register.csv", "Export benefit register")
