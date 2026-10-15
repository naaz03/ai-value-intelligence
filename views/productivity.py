from __future__ import annotations

import streamlit as st

from components.charts import bar_rank
from components.filters import current_filters
from components.kpi_cards import kpi_grid
from components.layout import page_note
from components.tables import download_csv, styled_table
from config.settings import SETTINGS
from services.metric_service import portfolio_kpis, productivity_summary
from services.roi_service import simulate
from utils.calculations import fte_equivalent
from utils.formatting import format_percent, safe_div


def render() -> None:
    filters = current_filters()
    k = portfolio_kpis(filters)
    page_note(
        "Operational improvement is not financial realization. Hours saved become FTE capacity; "
        "they become money only when a realization factor is applied."
    )
    kpi_grid(
        [
            {"label": "Hours saved", "value": k["hours_saved"], "kind": "hours"},
            {"label": "FTE capacity released", "value": k["fte_capacity"], "kind": "number", "decimals": 1, "help": f"{SETTINGS.working_hours_per_year:,} working hours / year"},
            {"label": "If fully cashed (not recommended)", "value": k["hours_saved"] * 45, "kind": "currency", "help": "Illustrative only at $45/hr — not booked as benefit"},
            {"label": "Realized value (actual)", "value": k["realized_value"], "kind": "currency", "help": "From the benefit register, not hours × wage"},
        ]
    )

    st.subheader("Realization factor")
    factor = st.slider("Share of capacity converted to economic value", 0.05, 0.80, SETTINGS.default_realization_factor, 0.05)
    hourly = st.slider("Assumed average hourly cost (USD)", 20, 120, 45, 5)
    illustrative = simulate(
        licenses=max(1, k["licensed_users"]),
        license_price=30,
        adoption_rate=k["adoption_rate"] or 0.4,
        hours_saved_per_user_year=safe_div(k["hours_saved"], max(k["active_users"], 1)),
        hourly_cost=hourly,
        realization_factor=factor,
        infrastructure_cost=0,
        training_cost=0,
        implementation_cost=0,
        success_rate=1.0,
        years=1,
    )
    st.caption(
        f"Applying a {format_percent(factor)} realization factor at ${hourly}/hr would imply "
        f"about ${illustrative['realized_value']:,.0f} of productivity-linked value — still a scenario, not a booking."
    )

    prod = productivity_summary(filters)
    if prod.empty:
        st.info("No sampled productivity observations in this filter.")
        return
    by_uc = (
        prod.groupby("use_case_name", as_index=False)
        .agg(
            baseline_task_minutes=("baseline_task_minutes", "mean"),
            ai_assisted_task_minutes=("ai_assisted_task_minutes", "mean"),
            tasks_completed=("tasks_completed", "sum"),
            hours_saved=("hours_saved", "sum"),
            quality_before=("quality_before", "mean"),
            quality_after=("quality_after", "mean"),
            rework_before=("rework_before", "mean"),
            rework_after=("rework_after", "mean"),
        )
        .sort_values("hours_saved", ascending=False)
    )
    by_uc["improvement_pct"] = 1 - by_uc["ai_assisted_task_minutes"] / by_uc["baseline_task_minutes"].replace(0, 1)
    by_uc["fte"] = by_uc["hours_saved"].apply(lambda h: fte_equivalent(h, SETTINGS.working_hours_per_year))
    st.plotly_chart(bar_rank(by_uc.head(15), "use_case_name", "hours_saved", "Hours saved by use case"), width="stretch")

    example = by_uc.iloc[0]
    st.markdown(
        f"**Before / after example — {example['use_case_name']}:** "
        f"{example['baseline_task_minutes']:.0f} minutes → {example['ai_assisted_task_minutes']:.0f} minutes "
        f"({format_percent(example['improvement_pct'])} faster). This is operational evidence, not a cash saving."
    )
    styled_table(by_uc.head(30))
    download_csv(by_uc, "productivity_by_use_case.csv")
