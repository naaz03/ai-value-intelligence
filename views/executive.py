from __future__ import annotations

import streamlit as st

from components.charts import bar_rank, bubble, funnel, line_trend
from components.executive_insights import render_insights
from components.filters import current_filters, current_persona
from components.kpi_cards import kpi_grid
from components.tables import download_csv, styled_table
from config.constants import PERSONAS, VALUE_CHAIN
from config.settings import SETTINGS
from services.metric_service import (
    investment_value_trend,
    portfolio_kpis,
    spend_by_dimension,
    usecase_performance,
)
from utils.formatting import format_currency, format_percent


def render() -> None:
    filters = current_filters()
    persona = current_persona()
    k = portfolio_kpis(filters)
    perf = usecase_performance(filters)
    st.markdown(
        f"""
<div class="exec-hero">
  <div class="exec-hero-label">The problem</div>
  <div class="exec-hero-text">
    {SETTINGS.organization_name} has invested <b>{format_currency(k["total_cost"])}</b> in AI,
    but usage dashboards cannot tell leadership whether that spend is creating value.
    Prompts are not productivity, hours saved are not cash, and adoption is not ROI.
  </div>
  <div class="exec-hero-label exec-hero-solution">The solution</div>
  <div class="exec-hero-text">
    AI Value Intelligence follows every dollar from investment to finance-realized value.
    Today <b>{format_currency(k["realized_value"])}</b> of
    {format_currency(k["potential_value"])} potential value is realized:
    <b>{format_percent(k["portfolio_roi"])} ROI</b> with
    ~{k["payback_months"]:.0f}-month payback, and
    <b>{format_currency(k["optimization_opportunity"])}</b> is recoverable from idle licenses.
  </div>
  <div class="exec-hero-label exec-hero-approach">Our approach</div>
  <div class="exec-hero-text">
    We measure every stage of the AI value chain, from investment and adoption to effective usage,
    operational improvement, and financial realization. Value is reported in three tiers:
    <b>Potential</b>, <b>Demonstrated</b>, and <b>Realized</b>. Only Realized counts toward ROI,
    and it is measured against the full cost of AI (licenses, infrastructure, implementation,
    training, support, security, and governance). Each of the {len(perf)} use cases is then
    ranked as Scale, Optimize, Monitor, Reassess, or Stop.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="chain-step">' + " → ".join(VALUE_CHAIN) + "</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"Persona lens: {persona}. {PERSONAS[persona]['description']}")

    focus = PERSONAS[persona]["focus"]
    catalog = {
        "net_benefit": {"label": "Net AI benefit", "value": k["net_benefit"], "kind": "currency", "help": "Realized value minus total AI cost"},
        "portfolio_roi": {"label": "Portfolio ROI", "value": k["portfolio_roi"], "kind": "percent", "help": "(Realized − Cost) / Cost"},
        "realized_value": {"label": "Realized AI value", "value": k["realized_value"], "kind": "currency", "help": "Captured and, where flagged, finance-relevant benefit"},
        "payback_months": {"label": "Payback period", "value": k["payback_months"], "kind": "months", "help": "Cost / average monthly realized value"},
        "value_realization_pct": {"label": "Value realization", "value": k["value_realization_pct"], "kind": "percent", "help": "Realized / Potential"},
        "finance_validated": {"label": "Finance-validated value", "value": k["finance_validated"], "kind": "currency"},
        "total_cost": {"label": "Total AI investment", "value": k["total_cost"], "kind": "currency", "help": "Licenses, infra, implementation, training, support, security, governance"},
        "active_users": {"label": "Active AI users", "value": k["active_users"], "kind": "int"},
        "adoption_rate": {"label": "AI adoption", "value": k["adoption_rate"], "kind": "percent", "help": "Active / licensed in latest month"},
        "underutilized_licenses": {"label": "Underutilized licenses", "value": k["underutilized_licenses"], "kind": "int"},
        "cost_per_active_user": {"label": "Cost per active user", "value": k["cost_per_active_user"], "kind": "currency"},
        "potential_value": {"label": "Potential value", "value": k["potential_value"], "kind": "currency"},
        "demonstrated_value": {"label": "Demonstrated value", "value": k["demonstrated_value"], "kind": "currency"},
        "production_use_cases": {"label": "Production use cases", "value": k["production_use_cases"], "kind": "int"},
        "high_performing": {"label": "High-performing use cases", "value": k["high_performing"], "kind": "int"},
        "hours_saved": {"label": "Hours saved", "value": k["hours_saved"], "kind": "hours", "help": "Operational capacity, not cash"},
        "fte_capacity": {"label": "FTE capacity released", "value": k["fte_capacity"], "kind": "number", "decimals": 1},
        "underperforming": {"label": "Underperforming use cases", "value": k["underperforming"], "kind": "int"},
        "optimization_opportunity": {"label": "License optimization", "value": k["optimization_opportunity"], "kind": "currency"},
        "infrastructure_cost": {"label": "Infrastructure cost", "value": k["infrastructure_cost"], "kind": "currency"},
        "cost_per_ai_task": {"label": "Cost per AI task", "value": k["cost_per_ai_task"], "kind": "currency"},
        "benefit_cost_ratio": {"label": "Benefit-cost ratio", "value": k["benefit_cost_ratio"], "kind": "number", "decimals": 2},
    }
    ordered = [catalog[key] for key in focus if key in catalog]
    extras = [
        catalog[key]
        for key in [
            "total_cost",
            "realized_value",
            "net_benefit",
            "portfolio_roi",
            "payback_months",
            "adoption_rate",
            "active_users",
            "potential_value",
            "demonstrated_value",
            "hours_saved",
            "fte_capacity",
            "underutilized_licenses",
            "optimization_opportunity",
            "production_use_cases",
            "high_performing",
            "underperforming",
        ]
        if key not in focus
    ]
    kpi_grid(ordered + extras, columns=4)

    trend = investment_value_trend(filters)
    left, right = st.columns(2)
    with left:
        if not trend.empty:
            st.plotly_chart(
                line_trend(trend, "month", ["total_cost", "realized_value"], "AI investment vs realized value"),
                width="stretch",
            )
    with right:
        if not trend.empty:
            st.plotly_chart(line_trend(trend, "month", ["roi"], "ROI trend"), width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            funnel(
                [
                    ("Potential", k["potential_value"]),
                    ("Demonstrated", k["demonstrated_value"]),
                    ("Realized", k["realized_value"]),
                ],
                "Potential → Demonstrated → Realized",
            ),
            width="stretch",
        )
    with c2:
        if not trend.empty:
            st.plotly_chart(line_trend(trend, "month", ["adoption_rate"], "Adoption trend"), width="stretch")

    spend_prod = spend_by_dimension(filters, "product_name")
    spend_bu = spend_by_dimension(filters, "business_unit_name")
    c3, c4 = st.columns(2)
    with c3:
        if not spend_prod.empty:
            st.plotly_chart(bar_rank(spend_prod.head(8), "product_name", "total_cost", "AI spend by product"), width="stretch")
    with c4:
        if not spend_bu.empty:
            st.plotly_chart(bar_rank(spend_bu, "business_unit_name", "realized_value", "Value by business unit"), width="stretch")

    if not spend_bu.empty:
        roi_bu = spend_bu.copy()
        roi_bu["roi"] = (roi_bu["realized_value"] - roi_bu["total_cost"]) / roi_bu["total_cost"].replace(0, 1)
        st.plotly_chart(bar_rank(roi_bu, "business_unit_name", "roi", "ROI by business unit"), width="stretch")

    if not perf.empty:
        t1, t2 = st.columns(2)
        with t1:
            st.subheader("Top 10 use cases by realized value")
            top = perf.head(10)[["use_case_name", "business_unit", "realized_value", "total_cost", "roi", "classification"]]
            styled_table(top)
        with t2:
            st.subheader("Bottom 10 use cases by ROI")
            bottom = perf.sort_values("roi").head(10)[["use_case_name", "business_unit", "realized_value", "total_cost", "roi", "classification"]]
            styled_table(bottom)
        bubble_src = perf.dropna(subset=["realized_value", "roi"]).copy()
        bubble_src["investment"] = bubble_src["total_cost"].clip(lower=1)
        if not bubble_src.empty:
            st.plotly_chart(
                bubble(bubble_src, "realized_value", "roi", "investment", "risk_rating", "use_case_name", "Use case portfolio matrix"),
                width="stretch",
            )
        download_csv(perf, "use_case_portfolio.csv", "Export use case portfolio")

    st.subheader("Executive insights")
    render_insights(filters, persona)

    kpi_export = pd_kpis(k)
    download_csv(kpi_export, "executive_kpis.csv", "Export KPI snapshot")


def pd_kpis(k: dict):
    import pandas as pd

    return pd.DataFrame([{"metric": key, "value": value} for key, value in k.items()])
