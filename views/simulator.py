from __future__ import annotations

import pandas as pd
import streamlit as st

from components.kpi_cards import kpi_grid
from components.layout import page_note
from components.tables import download_csv
from config.settings import SETTINGS
from services.metric_service import portfolio_kpis
from services.roi_service import simulate
from components.filters import current_filters
from utils.formatting import safe_div


def render() -> None:
    filters = current_filters()
    baseline = portfolio_kpis(filters)
    page_note(
        "Interactive planning model. Changing levers does not write back to the benefit register. "
        "Hours become money only through the realization factor."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        licenses = st.slider("Number of licenses", 500, 12_000, int(max(500, baseline["licensed_users"] or 4000)), 100)
        license_price = st.slider("License price (USD / user / month)", 5, 80, 30, 1)
        adoption = st.slider("Adoption rate", 0.10, 0.95, float(baseline["adoption_rate"] or 0.45), 0.01)
        hours = st.slider("Hours saved / active user / year", 10, 220, 48, 2)
    with c2:
        hourly = st.slider("Average employee hourly cost", 20, 150, 48, 2)
        realization = st.slider("Value realization %", 0.05, 0.90, SETTINGS.default_realization_factor, 0.05)
        success = st.slider("Use case success rate", 0.20, 1.00, 0.70, 0.05)
        years = st.slider("Planning horizon (years)", 1.0, 3.0, 1.0, 0.5)
    with c3:
        infra = st.number_input("Infrastructure cost", 0, 20_000_000, 1_200_000, 50_000)
        training = st.number_input("Training cost", 0, 5_000_000, 350_000, 25_000)
        impl = st.number_input("Implementation cost", 0, 10_000_000, 2_400_000, 50_000)
        support = st.number_input("Support + security + governance", 0, 8_000_000, 600_000, 25_000)

    result = simulate(
        licenses=licenses,
        license_price=license_price,
        adoption_rate=adoption,
        hours_saved_per_user_year=hours,
        hourly_cost=hourly,
        realization_factor=realization,
        infrastructure_cost=infra,
        training_cost=training,
        implementation_cost=impl,
        success_rate=success,
        support_cost=support * 0.5,
        security_cost=support * 0.3,
        governance_cost=support * 0.2,
        years=years,
    )
    kpi_grid(
        [
            {"label": "Projected cost", "value": result["projected_cost"], "kind": "currency"},
            {"label": "Gross productivity value", "value": result["gross_productivity_value"], "kind": "currency", "help": "Hours × wage, before realization"},
            {"label": "Demonstrated value", "value": result["demonstrated_value"], "kind": "currency"},
            {"label": "Realized value", "value": result["realized_value"], "kind": "currency"},
            {"label": "Net benefit", "value": result["net_benefit"], "kind": "currency"},
            {"label": "ROI", "value": result["roi"], "kind": "percent"},
            {"label": "Payback", "value": result["payback_months"], "kind": "months"},
            {"label": "Break-even users", "value": result["break_even_users"], "kind": "int"},
            {"label": "Active users", "value": result["active_users"], "kind": "int"},
            {"label": "Benefit-cost ratio", "value": result["benefit_cost_ratio"], "kind": "number", "decimals": 2},
        ]
    )
    st.caption(
        f"Gross hours {result['gross_hours']:,.0f}. Cash conversion uses realization {realization:.0%} "
        f"and success {success:.0%}. Current filtered realized value is a reference point only "
        f"(${baseline['realized_value']:,.0f})."
    )
    export = pd.DataFrame([result])
    download_csv(export, "simulator_scenario.csv", "Export scenario")
