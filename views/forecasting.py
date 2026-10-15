from __future__ import annotations

import streamlit as st

from components.charts import line_trend
from components.filters import current_filters
from components.layout import page_note
from components.tables import download_csv, styled_table
from services.forecasting_service import forecast_scenarios, scenario_totals
from utils.formatting import format_currency, format_percent


def render() -> None:
    filters = current_filters()
    page_note(
        "Scenarios are directional planning views, not guaranteed predictions. They extrapolate recent trends "
        "with conservative, base, and accelerated drifts."
    )
    horizon = st.slider("Horizon (months)", 12, 36, 24, 6)
    forecast = forecast_scenarios(filters, horizon=horizon)
    if forecast.empty:
        st.warning("Not enough history to forecast in the current filter.")
        return
    totals = scenario_totals(forecast)
    styled_table(totals)

    for scenario in ["Conservative", "Base", "Accelerated"]:
        subset = forecast[forecast["scenario"] == scenario]
        st.plotly_chart(
            line_trend(
                subset,
                "month",
                ["forecast_spend", "forecast_realized_value"],
                f"{scenario} scenario — spend vs realized value",
            ),
            width="stretch",
        )
        last = subset.iloc[-1]
        st.caption(
            f"{scenario}: ending adoption {format_percent(last['forecast_adoption'])}, "
            f"period spend {format_currency(subset['forecast_spend'].sum())}, "
            f"period realized {format_currency(subset['forecast_realized_value'].sum())}."
        )
    download_csv(forecast, "ai_value_forecast.csv")
